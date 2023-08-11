using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public class WaypointManager : MonoBehaviour
{
    public List<WaypointNode> waypoints = new List<WaypointNode>();
    public List<WaypointFollower> agents = new List<WaypointFollower>();
    [SerializeField] private int maxPathLength = 10;

    public GameObject characterPrefab; 
    public Transform parentObject; 
    public int numberOfCharacters = 5; 


    void Awake()
    {
        // Instantiate characters
        for (int i = 0; i < numberOfCharacters; i++)
        {
            GameObject charInstance = Instantiate(characterPrefab, Vector3.zero, Quaternion.identity, parentObject);
            WaypointFollower follower = charInstance.GetComponent<WaypointFollower>();
            if (follower)
            {
                agents.Add(follower);
            }
            Transform sphereTransform = charInstance.transform.Find("Sphere");
            MeshRenderer meshRenderer = sphereTransform.GetComponent<MeshRenderer>();
            Material rubberMaterial = meshRenderer.materials.FirstOrDefault(mat => mat.name.StartsWith("Character_Random_Mat"));
            Color randomColor = new Color(Random.value, Random.value, Random.value);
            rubberMaterial.SetColor("_Color", randomColor); // Randomize color

            Transform hatsParent = charInstance.transform.Find("Hats");
            int childrenCount = hatsParent.childCount;
            int randomHatIndex = Random.Range(0, childrenCount);
            for (int hatIndex = 0; hatIndex < childrenCount; hatIndex++)
            {
                Transform currentHat = hatsParent.GetChild(hatIndex);
                currentHat.gameObject.SetActive(hatIndex == randomHatIndex);
            }


        }

        foreach (var agent in agents)
        {
            agent.waypoints = GenerateRandomPath();
        }
    }

    private List<WaypointNode> GenerateRandomPath()
    {
        if (waypoints.Count == 0)
            return null;

        List<WaypointNode> randomPath = new List<WaypointNode>();

        // Start with a random waypoint.
        WaypointNode currentWaypoint = waypoints[Random.Range(0, waypoints.Count)];
        randomPath.Add(currentWaypoint);

        // Continue the path until a condition is met.
        while (randomPath.Count < maxPathLength)
        {
            // Fetch neighbors and filter out waypoints already in the path.
            var possibleNextWaypoints = currentWaypoint.neighbors.Where(n => !randomPath.Contains(n)).ToList();
            
            // If no possible neighbors, break out.
            if (!possibleNextWaypoints.Any())
                break;

            // Choose a random neighbor from the filtered list.
            currentWaypoint = possibleNextWaypoints[Random.Range(0, possibleNextWaypoints.Count)];
            randomPath.Add(currentWaypoint);
        }

        return randomPath;
    }


}
