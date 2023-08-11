using UnityEngine;

public class AudioAnimationHandler : MonoBehaviour
{
    private AudioSource audioSource;

    private void Start()
    {
        audioSource = GetComponent<AudioSource>();
    }

    public void PlaySpecificAudio(AudioClip clip)
    {
        audioSource.clip = clip;
        audioSource.Play();
    }
}