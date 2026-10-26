using System;
using System.IO;

namespace Demo
{
    class Program
    {
        static void Main(string[] args)
        {
            var p = new Program();
            p.Start();
            Helper.Run();
        }

        void Start()
        {
            this.Log("go");
            Console.WriteLine(File.Exists("x"));
        }

        void Log(string m)
        {
        }
    }

    static class Helper
    {
        public static void Run()
        {
        }
    }

    interface IRunner
    {
        void Run();
    }
}
