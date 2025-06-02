using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit.Inputs.Readers;
using System.Collections;
using System.Collections.Generic;

public class ControllerCapturer : MonoBehaviour
{
    public string remoteIP = "xxx.xxx.x.xx"; // Replace with your Python receiver's IP
    public int remotePort = 5005;

    private UdpClient udpClient;
    private IPEndPoint remoteEndPoint;

    private float sendInterval = 1f / 20f; // 20 Hz = every 0.05s
    private float sendTimer = 0f;
    [SerializeField]

    XRInputValueReader<float> m_GripInput = new XRInputValueReader<float>("Grip");

    [SerializeField]
    XRInputValueReader<float> m_TriggerInput = new XRInputValueReader<float>("Trigger");

    private Vector3 lastRot;

    void Start()
    {
        udpClient = new UdpClient();
        remoteEndPoint = new IPEndPoint(IPAddress.Parse(remoteIP), remotePort);
    }

    float CheckEnable()
    {
         if (m_GripInput == null)
        {
            Debug.LogWarning("Grip Input is not assigned!");
            return 0.0f;
        }

        var gripVal = m_GripInput.ReadValue();
        if (gripVal > 0.5f)
        {
            return 1.0f;
        }
        else{
            return 0.0f;
        }
    }

    float CheckTrigger(){
        if (m_TriggerInput == null)
        {
            Debug.LogWarning("Trigger Input is not assigned!");
            return 0.0f;
        }

        var gripVal = m_TriggerInput.ReadValue();
        if (gripVal > 0.5f)
        {
            return 1.0f;
        }
        else{
            return -1.0f;
        }
    }

    Vector3 FixRotation(Vector3 rot, Vector3? lastRot)
    {
        if (lastRot == null)
        {
            return rot;
        }

        Vector3 fixedRot = rot;

        if (rot.x - lastRot.Value.x > 180f)
        {
            fixedRot.x = -1f * (360f - rot.x);
        }

        if (rot.y - lastRot.Value.y > 180f)
        {
            fixedRot.y = -1f * (360f - rot.y);
        }

        if (rot.z - lastRot.Value.z > 180f)
        {
            fixedRot.z = -1f * (360f - rot.z);
        }

        return fixedRot;
    }

    Vector3 GetRotation()
    {
        return transform.rotation.eulerAngles;

    }

    void Update()
    {
        sendTimer += Time.deltaTime;
        if (sendTimer >= sendInterval)
        {
            sendTimer = 0f;

            Vector3 pos = transform.position;
            Quaternion rot = transform.rotation;

            /////////////////////

            Vector3 newRot = GetRotation();
            newRot = FixRotation(newRot, lastRot);
            lastRot = newRot;
            // Debug.Log(string.Format("{0},{1},{2}",
            //     newRot.x, newRot.y, newRot.z));
            /// /////////////////
            
            float enable = CheckEnable();
            float trigger = CheckTrigger();

            string message = string.Format("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}",
                pos.x, pos.z, pos.y, rot.x, rot.y, rot.z, rot.w, newRot.x, newRot.y, newRot.z, enable, trigger);
            Debug.Log(message);

            byte[] data = Encoding.UTF8.GetBytes(message);
            udpClient.Send(data, data.Length, remoteEndPoint);
        }
    }

    void OnApplicationQuit()
    {
        udpClient.Close();
    }
}
