<img align="right" width="100" style="margin-left: 20px; border-radius: 10px;" src="logos/logo.png" />

# 🛰️ CTF UniVsThreats: *Stellar Frequencies*

> **Event:** #CTF/UniVSThreats
>  **Points:** 100 | **Category:** #stego

---
## 📝 Challenge Description
> [!info] 
>A layered audio transmission masks a space message within a thin, high‑frequency band, buried under a carrier. With the right tuning, the faint signal resolves into a drifting cipher beyond the audible, like a relay echoing from deep space. Ready to hunt the signal and decode what’s hiding between the bands?

## 🛠️ Recon & Tools
- [/] **Files:** `frequencies.wav`
- [/] Sonic Visualiser [Windows/Linux]
- [/] Audacity [Windows/Linux]
- [ ] Python (optional)
- [/] Spectrogram analysis
## 🎨 STEGO 

#### Initial Recon:

The provided `.wav` file did not reveal anything obvious when played normally.  
Since the challenge description hints at **high-frequency bands**, the next step was to inspect the **spectrogram** of the audio.

>[!warning] **Stego:** Spectrogram

## 🚀 Exploitation Path

### 1️⃣ Initial Inspection

- Played the `.wav` file → nothing audible.
- Checked metadata and format:

```sh title:bash ln:false
ffprobe file_name.wav
```
- File looks normal; no embedded metadata or hidden channels detected.

### 2️⃣ Spectrogram Analysis (Manual)

#### **Windows / GUI Approach**

1. Open the file in **Sonic Visualiser**.
2. Enable **Spectrogram view**.
3. Adjust **gain** and **contrast** to enhance faint high-frequency signals.
4. Expand frequency scale to include the inaudible bands (e.g., 15–20 kHz).
5. The hidden text appears visually in the spectrogram.

#### Linux / Kali Approach
* Install Sonic Visualiser
```sh title:bash ln:false
sudo apt update
sudo apt install sonic-visualiser audacity sox
```
* Open the file
```sh title:bash ln:false
sonic-visualiser frequencies.wav
```
* Repeat same steps as above.

![[sonic_visualizer.png]]

### 3️⃣ Spectrogram Extraction via Python (Optional)

If you prefer a reproducible, automated approach:
```python title:"frequenciesAnalizer.py"
import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np

# Load WAV file
rate, data = wavfile.read("frequencies.wav")

# Convert to mono if stereo
if len(data.shape) > 1:
    data = data.mean(axis=1)

# Generate spectrogram
plt.specgram(data, Fs=rate, NFFT=2048, noverlap=1024, cmap='viridis')
plt.xlabel("Time [s]")
plt.ylabel("Frequency [Hz]")
plt.title("Spectrogram")
plt.colorbar(label="Intensity [dB]")
plt.show()
```
>  Once the spectrogram is plotted, visually inspect high-frequency regions for the hidden text.

![[python_visualizer.png]]

## 🏁 Flag

> [!success] Flag `UVT{5t4rsh1p_3ch03s_fr0m_th3_0ut3r_v01d}`

> [!faq]
> - This is a classic **audio steganography** challenge where the text is “drawn” in the **frequency domain**.
> - Direct listening does not reveal the message; spectrogram analysis is required.
> - Reproducible on any OS with Sonic Visualiser, Audacity, or Python.

