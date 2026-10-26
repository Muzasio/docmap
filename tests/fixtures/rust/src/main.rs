use std::fs;
mod net;

struct App {
    port: u16,
}

impl App {
    fn new() -> App {
        App { port: 8080 }
    }

    fn run(&self) {
        self.log("start");
        net::listen(self.port);
        let text = fs::read_to_string("x").unwrap();
        helper(&text);
    }

    fn log(&self, msg: &str) {
        println!("{}", msg);
    }
}

fn helper(s: &str) -> usize {
    s.len()
}

fn main() {
    let app = App::new();
    app.run();
}
