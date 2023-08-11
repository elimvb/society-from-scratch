using UnityEngine;

public class SlideshowControllerScript : MonoBehaviour
{
    private Animator animator;

    private void Start()
    {
        animator = GetComponent<Animator>();
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.RightArrow))
        {
            animator.SetTrigger("NextSlide");
        }
    }
}