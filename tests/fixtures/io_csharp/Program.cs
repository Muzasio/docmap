using System.IO;
using System.Diagnostics;
using Sys = System;

namespace Tools
{
    class Program
    {
        static void Main(string[] args)
        {
            string text = File.ReadAllText("notes.txt");
            File.WriteAllText(@"C:\temp\out.txt", text);
            var reader = new StreamReader("input.csv");
            Process.Start("git", "pull --rebase");
            Directory.CreateDirectory(args[0]);
            Sys.IO.File.Delete("old.log");
        }
    }
}
