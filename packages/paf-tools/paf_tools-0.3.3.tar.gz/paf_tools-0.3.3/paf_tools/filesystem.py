def CreateOrCleanDirectory(path):
    pass
    # System.IO.DirectoryInfo directory = new DirectoryInfo(path);
    """
    try:
        {
            if (!directory.Exists)
            {

                Directory.CreateDirectory(path);
            }
            else
            {
                foreach (FileInfo file in directory.__get_Files())
                {
                    file.Delete();
                }
            }
        }
    catch (Exception ex)
        {
            ////Logging_old.WriteLogError(ex.Message);
        }
        """
