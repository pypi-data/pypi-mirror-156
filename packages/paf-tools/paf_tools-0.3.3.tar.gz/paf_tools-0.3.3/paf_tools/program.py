"""
using System;

namespace As.It.Ses.Libraries.Tools
{
	public static class Program
	{
		public static bool CheckParameter(string[] arguments, int amount)
		{
			if (arguments.Length > 0)
			{
				if (arguments.Length != amount)
				{
					throw new Exception("Die Anzahl an Argumenten ist falsch, bitte prüfen! (Es sollten " + amount.ToString() + " Argumente angegeben werden)");
				}
			}
			else
			{
				return false;
			}

			return true;
		}
	}
}
"""