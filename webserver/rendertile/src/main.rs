// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
//
// Experimental helper for painting raster tiles
//
// The tool reads its input from stdin, and writes a PNG image to stdout.
// Input is consumed as a stream, so you can pass very large amounts of data.
//
// Sample input for a tile 9/268/179 with two layers in different colors:
//
//   T {"zoom":9, "x":268, "y":179}
//   L {"marker-fill":"#880033", "marker-width": 6.0}
//   P [15.417046, 47.07289]
//   P [8.723286, 47.499467]
//   L {"marker-fill":"#3300FF", "marker-width": 9.0}
//   P [8.7183005, 47.3505937]

use serde_json::Value;
use std::f64::consts::PI;
use std::io::{self, Write};
use tiny_skia::*;

struct Tile {
    zoom: u8,
    x: u32,
    y: u32,
    image: Pixmap,
    layer: Layer,
}

struct Layer {
    marker_color: ColorU8,
    marker_width: f32,
    foreground: Pixmap,
}

impl Tile {
    fn new(zoom: u8, x: u32, y: u32) -> Tile {
        return Tile {
            zoom,
            x,
            y,
            image: Pixmap::new(256, 256).unwrap(),
            layer: Layer::default(),
        };
    }

    fn draw_point(&mut self, lng: f64, lat: f64) {
        let n = (1_u64 << self.zoom) as f64;
        let xtile = (lng + 180.0) / 360.0 * n;
        let ytile = (1.0 - lat.to_radians().tan().asinh() / PI) / 2.0 * n;
        let x = (xtile - self.x as f64) * 256.0;
        let y = (ytile - self.y as f64) * 256.0;
        self.layer.draw_marker(x as f32, y as f32);
    }

    fn start_layer(&mut self, marker_color: ColorU8, marker_width: f32) {
        self.finish_layer();
        self.layer = Layer::new(marker_color, marker_width);
    }

    fn finish_layer(&mut self) {
        self.image.draw_pixmap(
            0,
            0,
            self.layer.foreground.as_ref(),
            &PixmapPaint::default(),
            Transform::identity(),
            None,
        );
    }

    fn encode_png(&self) -> Result<Vec<u8>, png::EncodingError> {
        return self.image.encode_png();
    }
}

impl Layer {
    fn default() -> Layer {
        Layer {
            marker_color: ColorU8::from_rgba(0, 0, 0, 0),
            marker_width: 1.0,
            foreground: Pixmap::new(1, 1).unwrap(),
        }
    }

    fn new(marker_color: ColorU8, marker_width: f32) -> Layer {
        Layer {
            marker_color: marker_color,
            marker_width: marker_width,
            foreground: Pixmap::new(256, 256).unwrap(),
        }
    }

    fn draw_marker(&mut self, x: f32, y: f32) {
        let mut paint = Paint::default();
        paint.anti_alias = true;

        let width = self.marker_width;
        let r = width / 2.0;
        let bbox = Rect::from_xywh(x - r, y - r, width, width).unwrap();
        let path = PathBuilder::from_oval(bbox).unwrap();
        paint.set_color_rgba8(
            self.marker_color.red(),
            self.marker_color.green(),
            self.marker_color.blue(),
            self.marker_color.alpha(),
        );
        self.foreground.fill_path(
            &path,
            &paint,
            FillRule::Winding,
            Transform::identity(),
            None,
        );
    }
}

fn main() -> io::Result<()> {
    let mut tile = Tile::new(0, 0, 0);

    for line in io::stdin().lines() {
        let l = line.unwrap();
        let (cmd, data) = l.split_at(1);
        let v: Value = serde_json::from_str(data)?;
        match cmd {
            "T" => {
                let params: Value = serde_json::from_str(data)?;
                tile.zoom = params["zoom"].as_i64().unwrap_or_default() as u8;
                tile.x = params["x"].as_i64().unwrap_or_default() as u32;
                tile.y = params["y"].as_i64().unwrap_or_default() as u32;
            }

            "L" => {
                let params: Value = serde_json::from_str(data)?;
                let color_str = params["marker-fill"].as_str().unwrap_or("");
                let color = parse_color(color_str.to_string());
                let width = params["marker-width"].as_f64();
                tile.start_layer(color.unwrap(), width.unwrap_or(6.0) as f32);
            }

            "P" => {
                let lng = v[0].as_f64().unwrap_or_default();
                let lat = v[1].as_f64().unwrap_or_default();
                tile.draw_point(lng, lat);
            }

            _ => panic!("unsupported command {}", cmd),
        }
    }
    tile.finish_layer();
    let png = tile.encode_png().unwrap();
    io::stdout().write_all(&png)?;
    Ok(())
}

fn parse_color(c: String) -> Option<tiny_skia::ColorU8> {
    let stripped = c.strip_prefix("#");
    if stripped.is_none() {
        return None;
    }

    let decoded = hex::decode(stripped.unwrap());
    if !decoded.is_ok() {
        return None;
    }

    let n = decoded.unwrap();
    match n.len() {
        3 => return Some(ColorU8::from_rgba(n[0], n[1], n[2], 255)),
        4 => return Some(ColorU8::from_rgba(n[0], n[1], n[2], 255)),
        _ => return None,
    }
}
