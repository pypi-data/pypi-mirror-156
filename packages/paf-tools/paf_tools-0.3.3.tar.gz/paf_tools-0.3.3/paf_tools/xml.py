import xmltodict


def to_dict(xml_string: str) -> dict:
    return xmltodict.parse(xml_string)


"""

	{
    public static ArrayList ToArrayList(XmlNodeList nodes)
    {
      var nodeArrayList = new ArrayList();
      foreach(var node in nodes)
      {
        nodeArrayList.Add(node.ToString());
      }
      return nodeArrayList;
    }
	}
}
namespace ExtensionMethods
{
  public static class MyExtensionMethods
  {
    public static ArrayList ToArrayList(this XmlNodeList nodes)
    {
      var nodeArrayList = new ArrayList();
      foreach(XmlNode node in nodes)
      {
        nodeArrayList.Add(((XmlElement)node).ToString());
      }
      return nodeArrayList;
    }
  }
}
"""
