pub fn usage() -> &'static str {
    "line one\n\
     line two"
}

pub fn after() -> &'static str {
    "x"
}

macro_rules! make {
    () => { fn made() {} };
}

pub fn noisy() {
    eprintln!("fn fake failed");
}
