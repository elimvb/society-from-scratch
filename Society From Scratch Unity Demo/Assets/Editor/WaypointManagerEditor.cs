using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(WaypointManager))]
public class WaypointManagerEditor : Editor
{
    public override void OnInspectorGUI()
    {
        WaypointManager manager = (WaypointManager)target;

        // Draw the default inspector
        DrawDefaultInspector();

        // Buttons for our custom tools
        if (GUILayout.Button("Link Nodes"))
        {
            LinkNodes(manager);
        }

        if (GUILayout.Button("Unlink Nodes"))
        {
            UnlinkNodes(manager);
        }
        if (GUILayout.Button("Reset"))
        {
            ResetNodes(manager);
        }
        

    }

    private void LinkNodes(WaypointManager manager)
    {
        // Get the selected objects
        Object[] selectedObjects = Selection.objects;

        if (selectedObjects.Length == 2)
        {
            WaypointNode node1 = ((GameObject)selectedObjects[0]).GetComponent<WaypointNode>();
            WaypointNode node2 = ((GameObject)selectedObjects[1]).GetComponent<WaypointNode>();

            if (node1 != null && node2 != null)
            {
                // Link both nodes together
                if (!node1.neighbors.Contains(node2))
                    node1.neighbors.Add(node2);
                if (!node2.neighbors.Contains(node1))
                    node2.neighbors.Add(node1);

                if (!manager.waypoints.Contains(node1))
                    manager.waypoints.Add(node1);
                if (!manager.waypoints.Contains(node2))
                    manager.waypoints.Add(node2);
            }
        }
        else
        {
            Debug.LogWarning("Please select exactly two nodes to link.");
        }
        RemoveUnlinkedNodes(manager);
    }

    private void UnlinkNodes(WaypointManager manager)
    {
        // Get the selected objects
        Object[] selectedObjects = Selection.objects;

        if (selectedObjects.Length == 2)
        {
            WaypointNode node1 = ((GameObject)selectedObjects[0]).GetComponent<WaypointNode>();
            WaypointNode node2 = ((GameObject)selectedObjects[1]).GetComponent<WaypointNode>();

            if (node1 != null && node2 != null)
            {
                // Remove links between nodes
                if (node1.neighbors.Contains(node2))
                    node1.neighbors.Remove(node2);
                if (node2.neighbors.Contains(node1))
                    node2.neighbors.Remove(node1);
                
                if (node1.neighbors.Count == 0 && manager.waypoints.Contains(node1))
                    manager.waypoints.Remove(node1);
                if (node2.neighbors.Count == 0 && manager.waypoints.Contains(node2))
                    manager.waypoints.Remove(node2);
            }
        }
        else
        {
            Debug.LogWarning("Please select exactly two nodes to unlink.");
        }
        RemoveUnlinkedNodes(manager);
    }
    private void ResetNodes(WaypointManager manager)
    {
        // Loop through all the nodes in the manager's list
        foreach (var node in manager.waypoints)
        {
            if (node)
            {
                node.neighbors.Clear(); // Remove all neighbors from each node
            }
        }
        
        manager.waypoints.Clear(); // Remove all nodes from the manager's list
    }
    private void RemoveUnlinkedNodes(WaypointManager manager)
    {
        // Debug.Log("Running remove unlink");
        for (int i = manager.waypoints.Count - 1; i >= 0; i--)
        {
            if (manager.waypoints[i].neighbors.Count == 0)
            {
                manager.waypoints.RemoveAt(i);
            }
        }
    }
}
