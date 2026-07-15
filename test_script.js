
            // Theme Management
            function toggleTheme() {
                const currentTheme = document.documentElement.getAttribute("data-theme");
                const newTheme = currentTheme === "dark" ? "light" : "dark";
                document.documentElement.setAttribute("data-theme", newTheme);
                localStorage.setItem("selectedTheme", newTheme);
                
                // Keep momSettings in sync
                let settings = JSON.parse(localStorage.getItem("momSettings")) || {};
                settings.theme = newTheme;
                localStorage.setItem("momSettings", JSON.stringify(settings));
            }
            
            // System status check
            window.onload = function() {
                const settings = JSON.parse(localStorage.getItem("momSettings")) || {};
                let savedTheme = settings.theme || localStorage.getItem("selectedTheme");
                
                if (!savedTheme || savedTheme === 'auto') {
                    savedTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
                }
                document.documentElement.setAttribute("data-theme", savedTheme);

                checkStatus();
                fetchModelConfig();
                
                // Show last generated MOM if redirected from settings
                if (window.location.search.includes('show_last=true')) {
                    const lastMOM = localStorage.getItem('lastGeneratedMOM');
                    const lastTranscript = localStorage.getItem('lastGeneratedTranscript');
                    if (lastMOM) {
                        document.getElementById('transcript').value = lastTranscript || '';
                        showResult('textResult', `<strong>Generated MOM (From Teams):</strong><br><br>${lastMOM.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>')}`);
                        document.getElementById('btnSaveText').style.display = 'block';
                        // Scroll to it
                        setTimeout(() => document.getElementById('textResult').scrollIntoView({behavior: 'smooth'}), 500);
                    }
                }
                setInterval(checkStatus, 30000);
            };
            
            function checkStatus() {
                fetch('/api/v1/status')
                    .then(r => r.json())
                    .then(data => {
                        let html = '';
                        let ollama_ok = data.services.ollama && data.services.ollama.status === 'running';
                        let whisper_ok = data.services.whisper && data.services.whisper.status === 'ready';
                        
                        html += ollama_ok ? '<div class="status-badge status-ok">🟢 AI Ready</div>' : 
                                '<div class="status-badge status-error">🔴 AI Offline</div>';
                        html += whisper_ok ? '<div class="status-badge status-ok">🟢 Whisper Ready</div>' : 
                                '<div class="status-badge status-error">🔴 Whisper Offline</div>';
                        
                        document.getElementById('status').innerHTML = html;
                    }).catch(e => {
                        document.getElementById('status').innerHTML = '<div class="status-badge status-error">🔴 Server Disconnected</div>';
                    });
            }
            
            function fetchModelConfig() {
                fetch('/api/v1/config')
                    .then(r => r.json())
                    .then(data => {
                        if(data.status === 'ok') {
                            const chunking = data.config.chunking_model || 'Not set';
                            const ollama = data.config.ollama_model || 'Not set';
                            const display = document.getElementById('modelConfigDisplay');
                            if(display) {
                                display.innerHTML = `Fast Layer: <strong>${chunking}</strong> &nbsp;|&nbsp; Refinement Layer: <strong>${ollama}</strong>`;
                            }
                        }
                    })
                    .catch(e => console.log('Error fetching config', e));
            }
            
            function setLoading(btnId, isLoading) {
                const btn = document.getElementById(btnId);
                if (!btn) return;
                if (isLoading) {
                    btn.classList.add('btn-loading');
                    btn.disabled = true;
                } else {
                    btn.classList.remove('btn-loading');
                    btn.disabled = false;
                }
            }
            
            function showResult(elementId, content, isError = false, isLoading = false) {
                const el = document.getElementById(elementId);
                el.className = 'result active' + (isError ? ' error' : '');
                
                if (isError) {
                    el.innerHTML = `<strong>Error:</strong> ${content}`;
                } else {
                    el.innerHTML = content.replace(/\\n/g, '<br>');
                }
                
                // Show/hide save button
                const btnId = 'btnSave' + elementId.replace('Result', '');
                const saveBtn = document.getElementById(btnId);
                if (saveBtn) {
                    saveBtn.style.display = (isError || isLoading) ? 'none' : 'inline-block';
                }
            }
            
            function saveMOMToFile(elementId, defaultFilename) {
                const el = document.getElementById(elementId);
                if (!el || !el.innerText) return;
                
                let textContent = el.innerText;
                const marker = "=== FINAL MINUTES OF MEETING ===";
                if(textContent.includes(marker)) {
                    textContent = textContent.split(marker)[1].trim();
                }
                
                const blob = new Blob([textContent], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = defaultFilename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
            
            async function exportToServer(elementId, format) {
                const el = document.getElementById(elementId);
                if (!el || !el.innerText) return;
                
                let textContent = el.innerText;
                const marker = "=== FINAL MINUTES OF MEETING ===";
                if(textContent.includes(marker)) {
                    textContent = textContent.split(marker)[1].trim();
                }
                
                const url = format === 'docx' ? '/api/v1/export/docx' : '/api/v1/export/pdf';
                const defaultFilename = 'meeting_mom.' + format;
                
                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: textContent})
                    });
                    if (!response.ok) throw new Error('Export failed');
                    
                    const blob = await response.blob();
                    const downloadUrl = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = downloadUrl;
                    a.download = defaultFilename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(downloadUrl);
                } catch(e) {
                    alert('Error exporting document: ' + e.message);
                }
            }
            
            // --- Live Streaming Logic ---
            let socket = null;
            if (typeof io !== 'undefined') {
                socket = io();
            } else {
                console.warn("Socket.IO not loaded. Live streaming requires internet access.");
            }
            
            function floatTo16BitPCM(input) {
                let output = new Int16Array(input.length);
                for (let i = 0; i < input.length; i++) {
                    let s = Math.max(-1, Math.min(1, input[i]));
                    output[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                }
                return output.buffer;
            }

            let audioContext;
            let mediaStream;
            let scriptProcessor;

            async function startLiveStreaming() {
                if (!socket) {
                    alert("Cannot start live stream. Socket.IO library failed to load (check internet connection).");
                    return;
                }
                try {
                    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
                    const source = audioContext.createMediaStreamSource(mediaStream);
                    
                    scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
                    
                    scriptProcessor.onaudioprocess = function(e) {
                        const inputData = e.inputBuffer.getChannelData(0);
                        const pcm16 = floatTo16BitPCM(inputData);
                        socket.emit('audio_chunk', pcm16);
                    };
                    
                    source.connect(scriptProcessor);
                    scriptProcessor.connect(audioContext.destination);
                    
                    document.getElementById('btnStartLive').disabled = true;
                    document.getElementById('btnStopLive').disabled = false;
                    document.getElementById('recIndicator').style.display = 'block';
                    
                    const el = document.getElementById('liveTranscript');
                    el.className = 'result active';
                    el.innerHTML = '';
                    
                } catch (err) {
                    alert('Error accessing microphone: ' + err.message);
                }
            }

            async function stopLiveStreaming() {
                if (scriptProcessor) {
                    scriptProcessor.disconnect();
                    scriptProcessor = null;
                }
                if (audioContext && audioContext.state !== 'closed') {
                    audioContext.close();
                }
                if (mediaStream) {
                    mediaStream.getTracks().forEach(track => track.stop());
                }
                document.getElementById('recIndicator').style.display = 'none';
                document.getElementById('btnStartLive').disabled = false;
                document.getElementById('btnStopLive').disabled = true;
                
                // Fetch final MOM
                const el = document.getElementById('liveTranscript');
                el.innerHTML += "\n\n[Generating Final MOM using Refinement Layer...]\n";
                el.scrollTop = el.scrollHeight;
                
                try {
                    const response = await fetch('/api/v1/generate-live-mom', { method: 'POST' });
                    const data = await response.json();
                    if(data.status === 'ok') {
                        el.innerHTML += "\n\n=== FINAL MINUTES OF MEETING ===\n\n" + data.mom;
                        document.getElementById('exportLiveGrp').style.display = 'flex';
                    } else {
                        el.innerHTML += "\n\nError generating MOM: " + data.error;
                    }
                } catch(e) {
                    el.innerHTML += "\n\nFailed to generate final MOM: " + e.message;
                }
                el.scrollTop = el.scrollHeight;
            }

            if (socket) {
                socket.on('transcript_update', function(data) {
                    const el = document.getElementById('liveTranscript');
                    el.innerHTML += data.text + " ";
                    // Scroll to bottom
                    el.scrollTop = el.scrollHeight;
                });
            }
            
            // --- End Live Streaming Logic ---
            
            // --- Microphone Recording Logic ---
            let recInterval;
            let recSeconds = 0;

            async function startRecording() {
                try {
                    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
                    const source = audioContext.createMediaStreamSource(mediaStream);
                    
                    scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
                    audioChunks = [];
                    
                    scriptProcessor.onaudioprocess = function(e) {
                        const inputData = e.inputBuffer.getChannelData(0);
                        audioChunks.push(new Float32Array(inputData));
                    };
                    
                    source.connect(scriptProcessor);
                    scriptProcessor.connect(audioContext.destination);
                    
                    document.getElementById('btnStartRec').disabled = true;
                    document.getElementById('btnStopRec').disabled = false;
                    document.getElementById('recIndicator').classList.add('active');
                    
                    const settings = JSON.parse(localStorage.getItem('momSettings')) || {};
                    const maxRecTime = (settings.audioMaxLength || 30) * 60;
                    
                    recSeconds = 0;
                    recInterval = setInterval(() => {
                        recSeconds++;
                        const m = Math.floor(recSeconds / 60).toString().padStart(2, '0');
                        const s = (recSeconds % 60).toString().padStart(2, '0');
                        document.getElementById('recTime').innerText = `${m}:${s}`;
                        
                        if (recSeconds >= maxRecTime) {
                            stopRecording();
                            alert(`Recording stopped at ${m}:${s} (max time reached)`);
                        }
                    }, 1000);
                    
                } catch (err) {
                    alert('Error accessing microphone: ' + err.message);
                }
            }

            function stopRecording() {
                if (scriptProcessor) {
                    scriptProcessor.disconnect();
                    scriptProcessor = null;
                }
                if (audioContext && audioContext.state !== 'closed') {
                    audioContext.close();
                }
                if (mediaStream) {
                    mediaStream.getTracks().forEach(track => track.stop());
                }
                
                clearInterval(recInterval);
                document.getElementById('recIndicator').classList.remove('active');
                document.getElementById('btnStartRec').disabled = false;
                document.getElementById('btnStopRec').disabled = true;
                
                processRecording();
            }

            function encodeWAV(samples) {
                const buffer = new ArrayBuffer(44 + samples.length * 2);
                const view = new DataView(buffer);
                
                const writeString = function(view, offset, string) {
                    for (let i = 0; i < string.length; i++) {
                        view.setUint8(offset + i, string.charCodeAt(i));
                    }
                };
                
                writeString(view, 0, 'RIFF');
                view.setUint32(4, 36 + samples.length * 2, true);
                writeString(view, 8, 'WAVE');
                writeString(view, 12, 'fmt ');
                view.setUint32(16, 16, true);
                view.setUint16(20, 1, true);
                view.setUint16(22, 1, true);
                view.setUint32(24, 16000, true);
                view.setUint32(28, 16000 * 2, true);
                view.setUint16(32, 2, true);
                view.setUint16(34, 16, true);
                writeString(view, 36, 'data');
                view.setUint32(40, samples.length * 2, true);
                
                let offset = 44;
                for (let i = 0; i < samples.length; i++, offset += 2) {
                    let s = Math.max(-1, Math.min(1, samples[i]));
                    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
                }
                
                return new Blob([view], { type: 'audio/wav' });
            }

            function processRecording() {
                if (audioChunks.length === 0) return;
                
                let totalLength = audioChunks.reduce((acc, val) => acc + val.length, 0);
                let samples = new Float32Array(totalLength);
                let offset = 0;
                for (let i = 0; i < audioChunks.length; i++) {
                    samples.set(audioChunks[i], offset);
                    offset += audioChunks[i].length;
                }
                
                const audioBlob = encodeWAV(samples);
                const template = document.getElementById('template-mic').value;
                const file = new File([audioBlob], "recorded_meeting.wav", { type: "audio/wav" });
                
                const settings = JSON.parse(localStorage.getItem('momSettings')) || {};
                const wordLimit = settings.momWordLimit || 300;
                
                const formData = new FormData();
                formData.append('audio', file);
                formData.append('template', template);
                formData.append('word_limit', wordLimit);
                
                showResult('micResult', 'Uploading and transcribing recording... This may take a moment.', false, true);
                document.getElementById('btnStartRec').disabled = true;
                
                fetch('/api/v1/generate', { method: 'POST', body: formData })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('btnStartRec').disabled = false;
                    if (data.status === 'success') {
                        const formattedMom = data.mom.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>');
                        showResult('micResult', `<strong>Minutes of Meeting:</strong><br><br>${formattedMom}`);
                    } else {
                        showResult('micResult', data.error, true);
                    }
                })
                .catch(e => {
                    document.getElementById('btnStartRec').disabled = false;
                    showResult('micResult', e.message, true);
                });
            }
            // ---------------------------------
            
            function generateMOM() {
                const file = document.getElementById('audioFile').files[0];
                const template = document.getElementById('template').value;
                
                if (!file) return alert('Please select an audio file');
                
                const settings = JSON.parse(localStorage.getItem('momSettings')) || {};
                const wordLimit = settings.momWordLimit || 300;
                
                const formData = new FormData();
                formData.append('audio', file);
                formData.append('template', template);
                formData.append('word_limit', wordLimit);
                
                setLoading('btnAudio', true);
                
                // Show multi-stage processing
                const stages = [
                    '⏳ Uploading and processing audio...',
                    '⏳ Transcribing with Whisper...',
                    '⏳ Generating structured MOM...',
                    '✨ Finalizing formatting...'
                ];
                let stageIdx = 0;
                showResult('momResult', `<strong>Status:</strong> ${stages[stageIdx]}`, false, true);
                
                const stageInterval = setInterval(() => {
                    stageIdx = Math.min(stageIdx + 1, stages.length - 1);
                    showResult('momResult', `<strong>Status:</strong> ${stages[stageIdx]}`, false, true);
                }, 15000); // Progress stage every 15s to simulate pipeline steps
                
                fetch('/api/v1/generate', { method: 'POST', body: formData })
                .then(r => r.json())
                .then(data => {
                    clearInterval(stageInterval);
                    setLoading('btnAudio', false);
                    if (data.status === 'success') {
                        const formattedMom = data.mom.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>');
                        showResult('momResult', `<strong>Minutes of Meeting:</strong><br><br>${formattedMom}`);
                    } else {
                        showResult('momResult', data.error, true);
                    }
                })
                .catch(e => {
                    setLoading('btnAudio', false);
                    showResult('momResult', e.message, true);
                });
            }
            
            function generateFromText() {
                const transcript = document.getElementById('transcript').value;
                const template = document.getElementById('template2').value;
                
                if (!transcript.trim()) return alert('Please paste a transcript');
                
                // Check text limit from settings
                const settings = JSON.parse(localStorage.getItem('momSettings')) || {};
                const maxChars = settings.textMaxLength || 10000;
                
                if (transcript.length > maxChars) {
                    alert(`Text exceeds maximum length of ${maxChars} characters. Current: ${transcript.length}`);
                    return;
                }
                
                setLoading('btnText', true);
                showResult('textResult', 'Generating MOM, please wait...', false, true);
                
                fetch('/api/v1/generate-from-text', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({transcript, template, word_limit: settings.momWordLimit || 300})
                })
                .then(r => r.json())
                .then(data => {
                    setLoading('btnText', false);
                    if (data.status === 'success') {
                        const formattedMom = data.mom.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>');
                        showResult('textResult', `<strong>Generated MOM:</strong><br><br>${formattedMom}`);
                    } else {
                        showResult('textResult', data.error, true);
                    }
                })
                .catch(e => {
                    setLoading('btnText', false);
                    showResult('textResult', e.message, true);
                });
            }

            // ─── MS Teams Integration ───────────────────────────────
            let teamsCredentials = null;

            function teamsShowStatus(msg, isError) {
                const el = document.getElementById('teamsConnStatus');
                el.style.display = 'block';
                el.style.background = isError
                    ? 'rgba(239,68,68,0.15)' : 'rgba(16,185,129,0.15)';
                el.style.color = isError ? '#EF4444' : '#10B981';
                el.style.border = `1px solid ${isError ? '#EF4444' : '#10B981'}`;
                el.innerText = msg;
            }

            function teamsGetCreds() {
                return {
                    client_id:     document.getElementById('teamsClientId').value.trim(),
                    api_key:       document.getElementById('teamsClientSecret').value.trim(),
                    tenant_id:     document.getElementById('teamsTenantId').value.trim() || 'common',
                };
            }

            function teamsTestConnection() {
                const creds = teamsGetCreds();
                if (!creds.client_id || !creds.api_key) {
                    teamsShowStatus('Please enter Client ID and Client Secret.', true);
                    return;
                }
                document.getElementById('btnTeamsTest').disabled = true;
                teamsShowStatus('Testing connection...', false);
                fetch('/api/v1/teams/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(creds)
                })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('btnTeamsTest').disabled = false;
                    if (data.status === 'success') {
                        teamsShowStatus('✅ ' + data.message, false);
                    } else {
                        teamsShowStatus('❌ ' + (data.error || 'Connection test failed.'), true);
                    }
                })
                .catch(e => {
                    document.getElementById('btnTeamsTest').disabled = false;
                    teamsShowStatus('❌ ' + e.message, true);
                });
            }

            function teamsConnect() {
                const creds = teamsGetCreds();
                if (!creds.client_id || !creds.api_key) {
                    teamsShowStatus('Please enter Client ID and Client Secret.', true);
                    return;
                }
                document.getElementById('btnTeamsConnect').disabled = true;
                teamsShowStatus('Connecting to Microsoft Teams...', false);
                fetch('/api/v1/teams/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(creds)
                })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('btnTeamsConnect').disabled = false;
                    if (data.status === 'success') {
                        teamsCredentials = creds;
                        teamsShowStatus('✅ Connected! Now paste a meeting link below.', false);
                        document.getElementById('teamsMeetingForm').style.display = 'block';
                    } else {
                        teamsShowStatus('❌ ' + (data.error || 'Authentication failed. Check your credentials.'), true);
                    }
                })
                .catch(e => {
                    document.getElementById('btnTeamsConnect').disabled = false;
                    teamsShowStatus('❌ ' + e.message, true);
                });
            }

            function teamsFetchMeeting() {
                const link = document.getElementById('teamsMeetingLink').value.trim();
                if (!link) { alert('Please paste a Teams meeting link.'); return; }
                if (!teamsCredentials) { alert('Please connect to MS Teams first.'); return; }

                const template   = document.getElementById('teamsMomTemplate').value;
                const settings   = JSON.parse(localStorage.getItem('momSettings')) || {};
                const word_limit = settings.momWordLimit || 300;

                const payload = {
                    ...teamsCredentials,
                    meeting_link: link,
                    template,
                    word_limit,
                };

                setLoading('btnFetchTeamsMOM', true);
                showResult('teamsResult', 'Fetching transcript & generating MOM...', false, true);

                fetch('/api/v1/teams/fetch-meeting', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                })
                .then(r => r.json())
                .then(data => {
                    setLoading('btnFetchTeamsMOM', false);
                    if (data.status === 'success' && data.mom) {
                        const fmt = data.mom.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>');
                        showResult('teamsResult', `<strong>Minutes of Meeting (Teams):</strong><br><br>${fmt}`);
                    } else if (data.warning) {
                        showResult('teamsResult', '⚠️ ' + data.warning + (data.transcript ? '<br><br><em>Transcript fetched but MOM generation failed.</em>' : ''), true);
                    } else {
                        showResult('teamsResult', data.error || 'Failed to fetch meeting.', true);
                    }
                })
                .catch(e => {
                    setLoading('btnFetchTeamsMOM', false);
                    showResult('teamsResult', e.message, true);
                });
            }
            // ────────────────────────────────────────────────────────
        