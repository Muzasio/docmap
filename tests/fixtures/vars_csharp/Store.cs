using System.IO;
using System.Diagnostics;

class Store
{
    const string Db = "store.db";
    static readonly string Backup = "backup.db";
    string current = "current.db";

    void Save(string path)
    {
        File.WriteAllText(path, "x");
    }

    void Work()
    {
        File.ReadAllText(Db);
        File.Copy(Db, Backup);
        File.Delete(current);
        var tool = "git";
        Process.Start(tool, "status");
        Save("notes.txt");
        this.Save(Db);
    }
}
