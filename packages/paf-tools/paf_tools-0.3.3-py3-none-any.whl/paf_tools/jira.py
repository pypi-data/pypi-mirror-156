
_assignee = None
_files = None
_components = None
_service = None
_status = None
_text = None
_type = None
_summary = None
_labels = None

def get_text():
	return _text

def set_text(text:str):
	global _text
	_text = text

def get_summary():
	global _summary
	return _summary

def set_summary(summary: str = None):
	global _summary
	if summary is None:
		return _summary

	_summary = summary

def Assignee(assignee: str = None):
	global _assignee
	if assignee is None:
		return _assignee
	_assignee = assignee

"""
def Type(string type):
			_type = TranslateJiraType(type);

def Type(Jiratype type):
			_type = type;
"""

def Service(service: str = None):
	global _service
	if service is None:
		return _service

	_service = service

def Status(status: int = None):
	global _status
	if status is None:
		return status
	_status = status


def Status(string type, string status):
			switch (type.ToLower())
				case "testfall":
				case "test":
				case "tf":
					_status = Jirastatus.testcase.TranlateTransition(status);
					break;

def Attachments(ArrayList files):
			NewAttachments(Convert.ToString(files.ToArray()));

def Attachments(params string[] files):
			NewAttachments(files);

def NewAttachments(params string[] files):
			if (_files.Length == 0) _files = files; else _files = _files.Union(files).ToArray();

def Components(ArrayList components):
			NewComponent(Convert.ToString(components.ToArray()));

def Components(params string[] components):
			NewComponent(components);

def NewComponent(params string[] components):
			if (_components.Length == 0) _components = components; else _components = _components.Union(components).ToArray();

def Labels(ArrayList labels):
			NewLabel(Convert.ToString(labels.ToArray()));

def Labels(params string[] labels):
			NewLabel(labels);

def NewLabel(params string[] labels):
			if (_labels.Length == 0) _labels = labels; else _labels = _labels.Union(labels).ToArray();

def GetById(string id):
			Task<string> ltskAufgabe = holeJirapunkt(ID);
			ltskAufgabe.Wait();
			return ltskAufgabe.Result;
			return null;

def Create(string assignee, Jiratype type, string summary, string text, string[] components, string service, string[] attachments):
			Task<string> createTask = CreateJiraIssue(assignee, type, summary, text, components, service, attachments);
			createTask.Wait();
			return createTask.Result;

def Create(string assignee, Jiratype type, string summary, string text, string[] components, string service):
			return Create(assignee, type, summary, text, components, service, new string[] { });

def Create():
			try
				# Zusammenfassung
				_ = Jira._summary ?? throw new Exception("Die Zusammenfassung für den Jirapunkt darf nicht leer sein");
				#	Text
				_ = Jira._text ?? throw new Exception("Der Text für den Jirapunkt darf nicht leer sein");

				if (Jira._type == 0)
					Jira._type = Jiratype.Bug;

				if (Jira._assignee is null)
					Jira._assignee = "sync_alm_tech";
				if (Jira._status == 0)
					Jira._status = 1;
				if (Jira._service is null)
					Jira._service = "Testmanagement";

				if (Jira._components is null)
					Jira._components = new[] { "Monitoring" };
				if (Jira._files is null)
					Jira._files = new string[] { };

				Task<string> createTask = CreateJiraIssue();
				if (createTask.Status != TaskStatus.Faulted)
					createTask.Wait();
					string jiraKey = createTask.Result;

					createTask = SetStatus(jiraKey, Jira._type, 0, Jira._status);
					createTask.Wait();
					Logging.write("Job ist abgeschlossen", Logging.Loglevels.Info);
					return jiraKey;
				else:
					Logging.write("Konnte keinen neuen Jira-Punkt erzeugen!", Logging.Loglevels.Info);

			catch (Exception ex)
				Logging.WriteLogError(ex.Message);
			return null;


"""
//		//async private static Task<string> CreateJiraIssue()
//		//{
//			//Configuration.credentials jiraLoginData = Configuration.set_login_credentials("as_Jira");
//      //return null;

//			//var jiraInstance = gbibJira.jira.CreateRestClient(Configuration.Misc("Jira_URL"), jiraLoginData.user, jiraLoginData.password);
//			//var jiraIssue = jiraInstance.CreateIssue("MSDU");

//			//jiraIssue.Type = TranslateJiraType(_type);
//			//jiraIssue.Summary = _summary;
//			//jiraIssue.Assignee = _assignee;

//			//foreach (string component in _components) jiraIssue.Components.Add(component);

//			//jiraIssue["Service"] = _service;
//			//jiraIssue.Description = _text;

//			//if (_labels != null && _labels.Length > 0)
//			//{
//			//	foreach (string label in _labels) jiraIssue.labels.Add(label);
//			//}

//			//await jiraIssue.SaveChangesAsync();

//			//if (_files.Length > 0)
//			//{
//			//	foreach (string file in _files)
//			//	{
//			//		byte[] fileAsByte = File.ReadAllBytes(file);

//			//		jiraIssue.AddAttachment(file, fileAsByte);
//			//	}
//			//}

//			//await jiraIssue.SaveChangesAsync();

//			//return jiraIssue.Key.ToString();
////		}

//		async private static Task<string> SetStatus(string id, Jiratype type, int currentStatus, int destinationStatus)
//		{
//			string[] workflow = new string[] { };

//			switch (type)
//			{
//				case Jiratype.testcase:
//					switch (currentStatus)
//					{
//						case 0:
//							switch (destinationStatus)
//							{
//								case Jirastatus.testcase.Closed:
//									workflow = Jirastatus.testcase.OpenToClosed;
//									break;

//								case Jirastatus.testcase.InProgress:
//									workflow = Jirastatus.testcase.OpenToInProgress;
//									break;

//								case Jirastatus.testcase.Waiting:
//									workflow = Jirastatus.testcase.OpenToWaiting;
//									break;

//								case Jirastatus.testcase.Blocked:
//									workflow = Jirastatus.testcase.OpenToBlocked;
//									break;

//								case Jirastatus.testcase.Failed:
//									workflow = Jirastatus.testcase.OpenToFailed;
//									break;

//								case Jirastatus.testcase.Passed:
//									workflow = Jirastatus.testcase.OpenToPassed;
//									break;
//							}
//							break;
//					}
//					break;
//			}
//			try
//			{
//				Configuration.credentials jiraLoginData = Configuration.set_login_credentials("as_Jira");
//				//var jiraInstance = gbibJira.jira.CreateRestClient(
//				//		Configuration.Misc("Jira_URL"),
//				//		jiraLoginData.user,
//				//		jiraLoginData.password);

//				// use LINQ syntax to retrieve issues
//				//var jiraIssues = from i in jiraInstance.Issues.Queryable
//				//										 where i.Key == id
//				//										 orderby i.Created
//				//										 select i;

//				//foreach (gbibJira.Issue jiraIssue in jiraIssues)
//				//{
//				//	foreach (string transition in workflow)
//				//	{
//				//		await jiraIssue.WorkflowTransitionAsync(transition);
//				//		await jiraIssue.SaveChangesAsync();
//				//	}
//				//}

//				return string.Empty;
//			}
//			catch (Exception ex)
//			{
//				Logging.WriteLogError(ex.Message);
//			}
//			return null;
//		}

//		private static Jiratype TranslateJiraType(string type)
//		{
//			switch (type.ToLower())
//			{
//				case "fehler":
//				case "f":
//				case "bug":
//					return Jiratype.bug;
//				case "story":
//				case "s":
//					return Jiratype.story;
//				case "epic":
//				case "e":
//				case "epos":
//					return Jiratype.epic;
//				case "aufgabe":
//				case "a":
//				case "task":
//					return Jiratype.task;
//				case "testcase":
//				case "t":
//				case "tc":
//				case "testfall":
//				case "tf":
//				case "test":
//					return Jiratype.testcase;
//				default:
//					return Jiratype.task;
//			}
//		}
//		private static string TranslateJiraType(Jiratype type)
//		{
//			switch (type)
//			{
//				case Jiratype.bug:
//					return "Bug";

//				case Jiratype.story:
//					return "Story";

//				case Jiratype.epic:
//					return "Epic";

//				case Jiratype.test:
//					return "Test";

//				case Jiratype.task:
//					return "Task";

//				case Jiratype.testcase:
//					return "testcase";
//			}
//			return "Aufgabe";
//		}

//		public static class Jirastatus
//		{
//			public static class Testcase
//			{
//				public const int Blocked = 4;
//				public const int Passed = 6;
//				public const int Failed = 5;
//				public const int Closed = 1;
//				public const int InProgress = 2;
//				public const int Open = 0;
//				public const int Waiting = 3;
//				public static string[] OpenToBlocked = new string[] { "⇨ Test starten", "⇨ wird blockiert" };
//				public static string[] OpenToPassed = new string[] { "⇨ Test starten", "⇨ Test erfolgreich" };
//				public static string[] OpenToFailed = new string[] { "⇨ Test starten", "⇨ Fehler gefunden" };
//				public static string[] OpenToClosed = new string[] { "⇨ wird nicht ausgeführt" };
//				public static string[] OpenToInProgress = new string[] { "⇨ Test starten" };
//				public static string[] OpenToWaiting = new string[] { "⇨ Test starten", "⇨ müssen warten" };
//				public static string[] TranslateTransition(string name)
//				{
//					switch (name.ToLower())
//					{
//						case "offen_blockiert":
//						case "ob":
//							return new string[] { "⇨ Test starten", "⇨ wird blockiert" };
//						case "offen_erfolgreich":
//						case "oe": return new string[] { "⇨ Test starten", "⇨ Test erfolgreich" };
//						case "offen_fehlgeschlagen":
//						case "of": return new string[] { "⇨ Test starten", "⇨ Fehler gefunden" };
//						case "offen_geschlossen":
//						case "og": return new string[] { "⇨ wird nicht ausgeführt" };
//						case "offen_inbearbeitung":
//						case "oi":
//						case "oib": return new string[] { "⇨ Test starten" };
//						case "offen_wartend":
//						case "ow": return new string[] { "⇨ Test starten", "⇨ müssen warten" };
//						default: return new string[] { "⇨ Test starten", "⇨ Test erfolgreich" };
//					}
//				}
//				public static int TranlateTransition(string name)
//				{
//					switch (name.ToLower())
//					{
//						case "blockiert":
//						case "blocked":
//						case "b": return 4;
//						case "erfolgreich":
//						case "e":
//						case "passed": return 6;
//						case "fehlgeschlagen":
//						case "failed":
//						case "f": return 5;
//						case "geschlossen":
//						case "g":
//						case "closed": return 1;
//						case "inbearbeitung":
//						case "in bearbeitung":
//						case "inprogress":
//						case "in progress":
//						case "ib": return 2;
//						case "offen":
//						case "open":
//						case "o": return 0;
//						case "wartend":
//						case "waiting":
//						case "w": return 3;
//						default: return 0;
//					}
//				}
//			}
//		}
	}
}
"""