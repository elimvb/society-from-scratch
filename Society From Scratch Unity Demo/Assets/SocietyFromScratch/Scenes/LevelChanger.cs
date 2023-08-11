using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class LevelChanger : MonoBehaviour
{
    public Image fadePanel;
    public float fadeSpeed = 1.5f;

    private void Start()
    {
        // Start the scene by fading in
        StartCoroutine(FadeIn());
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            if (SceneManager.GetActiveScene().name == "Scene 1 - Generation") {
                FadeToScene("Scene 2 - Speed Dating");
            } else if (SceneManager.GetActiveScene().name == "Scene 2 - Speed Dating") {
                FadeToScene("Scene 1 - Generation");
            }
        }
    }

    public void FadeToScene(string sceneName)
    {
        StartCoroutine(FadeOut(sceneName));
    }

    IEnumerator FadeIn()
    {
        float alpha = fadePanel.color.a;
        while (alpha > 0f)
        {
            alpha -= fadeSpeed * Time.deltaTime;
            fadePanel.color = new Color(0, 0, 0, alpha);
            yield return null;
        }
    }

    IEnumerator FadeOut(string sceneName)
    {
        float alpha = fadePanel.color.a;
        while (alpha < 1f)
        {
            alpha += fadeSpeed * Time.deltaTime;
            fadePanel.color = new Color(0, 0, 0, alpha);
            yield return null;
        }

        // Once the fade out is complete, load the new scene
        SceneManager.LoadScene(sceneName);
    }
}
