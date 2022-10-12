// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
//
// Experimental helper for painting raster tiles
//
// Currently, this emits a PNG image with random dots to stdout.
// TODO: Instead of painting random dots, take data from stdin.

use std::io::{self, Write};
use tiny_skia::*;
use tinyrand::{Rand, StdRand};

fn main() -> io::Result<()> {
    let mut dots = Pixmap::new(256, 256).unwrap();
    let mut halos = Pixmap::new(256, 256).unwrap();

    let mut dot_paint = Paint::default();
    dot_paint.set_color_rgba8(0xff, 0x00, 0x66, 0xff);
    dot_paint.anti_alias = true;
    let dot = create_dot(6.0, dot_paint);

    let mut halo_paint = Paint::default();
    halo_paint.set_color_rgba8(0x00, 0x00, 0x00, 0xff);
    halo_paint.anti_alias = true;
    let halo = create_dot(8.0, halo_paint);

    let mut rand = StdRand::default();
    let dot_offset = (dot.width() / 2) as i32;
    let halo_offset = (halo.width() / 2) as i32;
    for _ in 0..300 {
        let x = (rand.next_u32() & 0xff) as i32;
        let y = (rand.next_u32() & 0xff) as i32;
        dots.draw_pixmap(
            x - dot_offset,
            y - dot_offset,
            dot.as_ref(),
            &PixmapPaint::default(),
            Transform::identity(),
            None,
        );
        halos.draw_pixmap(
            x - halo_offset,
            y - halo_offset,
            halo.as_ref(),
            &PixmapPaint::default(),
            Transform::identity(),
            None,
        );
    }

    halos.draw_pixmap(
        0,
        0,
        dots.as_ref(),
        &PixmapPaint::default(),
        Transform::identity(),
        None,
    );

    halos.save_png("image.png").unwrap();

    let png = halos.encode_png().unwrap();
    io::stdout().write_all(&png)?;
    Ok(())
}

fn create_dot(size: f32, paint: Paint) -> Pixmap {
    let bbox = Rect::from_xywh(0.0, 0.0, size, size).unwrap();
    let path = PathBuilder::from_oval(bbox).unwrap();

    let size_i32 = size.ceil() as u32;
    let mut pixmap = Pixmap::new(size_i32, size_i32).unwrap();
    pixmap.fill_path(
        &path,
        &paint,
        FillRule::Winding,
        Transform::identity(),
        None,
    );
    pixmap
}
