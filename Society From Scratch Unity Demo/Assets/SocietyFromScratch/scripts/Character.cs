using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Character : MonoBehaviour
{
    [SerializeField] private string[] texts;
    [SerializeField] private int textIndex = -1;

    SpeechBubble bubble;

    void Awake(){
        SpeechBubble[] bubbles = GetComponentsInChildren<SpeechBubble>();
        if (bubbles.Length > 0)
        {
            bubble = bubbles[0];
        }
        else
        {
            Debug.LogWarning("No SpeechBubble components found in children!");
        }
    }

    // void Update()
    // {
    //     if(textIndex >= 0 && textIndex<texts.Length) {
    //         bubble.SetText(texts[textIndex]);
    //         bubble.Show(true);
    //     } else {
    //         bubble.Show(false);
    //     }
    // }
}
