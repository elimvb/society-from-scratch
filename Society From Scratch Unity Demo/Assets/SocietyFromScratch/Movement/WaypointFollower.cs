using UnityEngine;
using System.Collections.Generic;

public class WaypointFollower : MonoBehaviour
{
    public List<WaypointNode> waypoints = new List<WaypointNode>();
    int currentWP = 0;

    public float speed = 10.0f;

    // Start is called before the first frame update
    void Start()
    {
        if (waypoints != null && waypoints.Count > 0)
        {
            Vector3 newPos = new Vector3(waypoints[0].transform.position.x, -0.429f, waypoints[0].transform.position.z);
            this.transform.position = newPos;

        }
    }

    // Update is called once per frame
    void Update()
    {
        if (Vector3.Distance(this.transform.position, waypoints[currentWP].transform.position) < 3)
            currentWP++;
        
        if (currentWP >= waypoints.Count){
            currentWP = 0;
            waypoints.Reverse();
        }
            

        Vector3 lookPosition = waypoints[currentWP].transform.position;
        lookPosition.y = transform.position.y; // set y value to the character's y value
        this.transform.LookAt(lookPosition);
        this.transform.Translate(0, 0, speed * Time.deltaTime);
    }
}
