using UnityEngine;

public class MapControllerScript : MonoBehaviour
{
    private Animator animator;

    private void Start()
    {
        animator = GetComponent<Animator>();
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.LeftControl))
        {
            animator.SetTrigger("NextSlide");
        }
    }
}