using UnityEngine;
using System.Collections.Generic;

public class WaypointNode : MonoBehaviour
{
    public List<WaypointNode> neighbors = new List<WaypointNode>();
    private WaypointNode originalNode;

    // void OnValidate()
    // {
    //     // Check if it's a new duplicate node.
    //     if (originalNode != this && neighbors.Count > 0 && !Application.isPlaying)
    //     {
    //         originalNode = this;
    //         neighbors.Clear();
    //     }
    // }
    // void Awake()
    // {
    //     if (originalNode == null)
    //     {
    //         originalNode = this;
    //     }
    // }

    void OnDrawGizmos()
    {
        Gizmos.color = Color.blue; 
        foreach (WaypointNode neighbor in neighbors)
        {
            
            Gizmos.DrawLine(transform.position, neighbor.transform.position);
            
        }

        Gizmos.color = Color.red; 
        Gizmos.DrawSphere(transform.position, 1.5f);
    }
}
