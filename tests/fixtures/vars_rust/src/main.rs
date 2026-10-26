use std::fs;

const CONFIG: &str = "app.toml";
static mut SCRATCH: &str = "tmp.txt";

fn write_log(path: &str, text: &str) {
    let _ = fs::write(path, text);
}

fn load() {
    let name = "data.json";
    let _ = fs::read_to_string(name);
    let _ = fs::read_to_string(CONFIG);
    let mut out = "a.txt";
    out = "b.txt";
    let _ = fs::write(out, "x");
    let _ = unsafe { fs::remove_file(SCRATCH) };
}

fn main() {
    load();
    write_log("events.log", "hi");
    let other = String::from("dyn.log");
    write_log(&other, "hi");
}

mod tests {
    fn helper_test() {
        let p = "t.txt";
        let _ = std::fs::read(&p);
    }
}
