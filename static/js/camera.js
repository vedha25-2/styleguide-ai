/**
 * StyleGuide AI - Camera Capture Module
 * Provides camera streaming, photo capture, and fallback handling
 */

let activeStream = null;

async function startCamera(videoElementId, errorContainerId = null) {
  const video = document.getElementById(videoElementId);
  if (!video) return;

  if (activeStream) {
    stopCamera(videoElementId);
  }

  try {
    const constraints = {
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: 'user'
      },
      audio: false
    };

    activeStream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = activeStream;
    await video.play();

    if (errorContainerId) {
      const errBox = document.getElementById(errorContainerId);
      if (errBox) errBox.classList.add('d-none');
    }
  } catch (err) {
    console.error('Camera access error:', err);
    if (errorContainerId) {
      const errBox = document.getElementById(errorContainerId);
      if (errBox) {
        errBox.classList.remove('d-none');
        errBox.innerHTML = `
          <div class="alert alert-warning d-flex align-items-center mb-2" role="alert">
            <i class="fa-solid fa-triangle-exclamation me-2 fs-5"></i>
            <div>
              <strong>Camera unavailable or permission denied.</strong><br>
              Please allow camera access in your browser settings or choose <em>"Upload from Gallery"</em> instead.
            </div>
          </div>
        `;
      }
    }
  }
}

function captureSnapshot(videoElementId, canvasElementId, hiddenInputId, previewImgId = null) {
  const video = document.getElementById(videoElementId);
  const canvas = document.getElementById(canvasElementId);
  const hiddenInput = document.getElementById(hiddenInputId);
  const previewImg = previewImgId ? document.getElementById(previewImgId) : null;

  if (!video || !canvas || !hiddenInput) return false;

  const w = video.videoWidth || 640;
  const h = video.videoHeight || 480;
  canvas.width = w;
  canvas.height = h;

  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, w, h);

  // Export as high quality JPEG DataURL
  const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
  hiddenInput.value = dataUrl;

  if (previewImg) {
    previewImg.src = dataUrl;
    previewImg.classList.remove('d-none');
  }

  return true;
}

function stopCamera(videoElementId) {
  const video = document.getElementById(videoElementId);
  if (activeStream) {
    activeStream.getTracks().forEach(track => track.stop());
    activeStream = null;
  }
  if (video) {
    video.srcObject = null;
  }
}

// Global cleanup when modals close
window.addEventListener('beforeunload', () => {
  if (activeStream) {
    activeStream.getTracks().forEach(track => track.stop());
  }
});
