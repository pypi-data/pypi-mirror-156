using System.IO;

namespace As.It.Ses.Libraries.Tools
{
	public static class Windows
	{
		/// <summary>Methode <c>Download_Ordner</c> gibt den Pfad zum Download-Ordner des aktuellen Benutzers zurück</summary>
		/// <returns>(string) - Pfad zum Download-Ordner des aktuellen Benutzers</returns>
		/// <example></example>
		///         
		public static string FolderDownload =  System.Convert.ToString(          
      Microsoft.Win32.Registry.GetValue(
      		@"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
      		, "{374DE290-123F-4565-9164-39C4925E467B}"
      		, string.Empty)
      );
		public static string FolderDesktop = System.Convert.ToString(
      Microsoft.Win32.Registry.GetValue(
      		@"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
      		, "{Desktop}"
      		, string.Empty)
      );
    public static string FolderDocuments = System.Convert.ToString(
      Microsoft.Win32.Registry.GetValue(
      		@"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
      		, "{Desktop}"
      		, string.Empty)
      );
    public static string ApplicationPath = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location);
		public static string FolderConfiguration = Path.Combine("C:\\", "AS_Programme", "Konfiguration");
	}
}
