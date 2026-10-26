pub trait Handler {
    fn handle(&self, data: &[u8]);
}

pub fn listen(port: u16) {
    open_socket(port);
}

fn open_socket(port: u16) -> bool {
    port > 0
}
