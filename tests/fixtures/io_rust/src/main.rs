use std::fs::{self, File};
use std::process::Command;
use std::io::Write as _;

fn save(path: &str) {
    fs::write("out.txt", "hi").unwrap();
    std::fs::remove_file(path).unwrap();
    let _f = File::open("in.txt");
}

fn run() {
    let _o = Command::new("ls").arg("-l").arg("/tmp").output();
    fs::copy("a.txt", "b.txt").unwrap();
}

fn main() {
    save("x");
    run();
}
