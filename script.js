// Estado de la aplicación
const appState = {
    selectedFiles: [],
    isProcessing: false,
    quality: 85,
    preserveMetadata: false,
    stats: {
        originalSize: 0,
        optimizedSize: 0,
        savedSize: 0,
        filesCount: 0,
        percentage: 0
    }
};

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    loadSettings();
    setupEventListeners();
    drawHeaderCanvas();
    drawProgressRing(0);
});

// Redibujar canvas al cambiar tamaño de ventana
window.addEventListener('resize', () => {
    const canvas = document.getElementById('headerCanvas');
    canvas.width = window.innerWidth;
    drawHeaderCanvas();
});

// Inicializar aplicación
function initializeApp() {
    // Intentar cargar logo
    const logoImg = document.getElementById('logoImage');
    const logoPaths = ['logo.png', 'logo.jpg', 'assets/logo.png', 'images/logo.png'];
    
    for (const path of logoPaths) {
        const img = new Image();
        img.onload = () => {
            logoImg.src = path;
            logoImg.style.display = 'block';
        };
        img.src = path;
        if (img.complete) break;
    }
}

// Dibujar canvas del header
function drawHeaderCanvas() {
    const canvas = document.getElementById('headerCanvas');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    
    // Líneas decorativas superiores
    for (let i = 0; i < 6; i++) {
        const y = 12 + i * 4;
        const gradient = 15 + i * 15;
        ctx.strokeStyle = `rgb(${gradient}, ${gradient}, ${Math.min(gradient + 20, 60)})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }
    
    // Líneas decorativas inferiores (después del texto)
    const centerX = width / 2;
    const lineWidth = 400;
    const startX = centerX - (lineWidth / 2);
    const endX = centerX + (lineWidth / 2);
    
    // Línea naranja
    ctx.fillStyle = '#ff6b35';
    ctx.fillRect(startX, 120, lineWidth, 3);
    
    // Línea cyan
    ctx.fillStyle = '#00f5ff';
    ctx.fillRect(startX + 2, 125, lineWidth - 4, 1);
}

// Dibujar anillo de progreso
function drawProgressRing(percentage) {
    const canvas = document.getElementById('progressRing');
    const ctx = canvas.getContext('2d');
    const size = 220;
    const center = size / 2;
    const radius = (size - 40) / 2;
    
    ctx.clearRect(0, 0, size, size);
    
    // Círculos de fondo
    for (let i = 4; i > 0; i--) {
        ctx.strokeStyle = '#1a1f3a';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(center, center, radius + i * 3, 0, Math.PI * 2);
        ctx.stroke();
    }
    
    // Arco de fondo
    ctx.strokeStyle = '#1a1f3a';
    ctx.lineWidth = 14;
    ctx.beginPath();
    ctx.arc(center, center, radius, 0, Math.PI * 2);
    ctx.stroke();
    
    // Arco de progreso
    if (percentage > 0) {
        const angle = (percentage / 100) * Math.PI * 2;
        const segments = Math.max(Math.floor(percentage / 4), 1);
        
        for (let i = 0; i < segments; i++) {
            const startAngle = -Math.PI / 2 + (i / segments) * angle;
            const endAngle = -Math.PI / 2 + ((i + 1) / segments) * angle;
            const color = getGradientColor(i / Math.max(segments - 1, 1));
            
            ctx.strokeStyle = color;
            ctx.lineWidth = 14;
            ctx.beginPath();
            ctx.arc(center, center, radius, startAngle, endAngle);
            ctx.stroke();
        }
        
        // Punto indicador
        const pointAngle = -Math.PI / 2 + angle;
        const px = center + radius * Math.cos(pointAngle);
        const py = center + radius * Math.sin(pointAngle);
        
        ctx.fillStyle = '#00f5ff';
        ctx.strokeStyle = '#00b8d4';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(px, py, 7, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(px, py, 3, 0, Math.PI * 2);
        ctx.fill();
    }
    
    // Texto central con sombra
    ctx.font = 'bold 40px Consolas';
    ctx.fillStyle = '#0a0e27';
    ctx.textAlign = 'center';
    ctx.fillText(`${Math.round(percentage)}%`, center + 2, center - 8);
    
    ctx.fillStyle = '#00f5ff';
    ctx.fillText(`${Math.round(percentage)}%`, center, center - 10);
    
    ctx.font = 'bold 11px Consolas';
    ctx.fillStyle = '#6c7a89';
    ctx.fillText('REDUCCIÓN', center, center + 25);
    
    // Marcadores decorativos
    for (let angle = 0; angle < 360; angle += 30) {
        const rad = (angle * Math.PI) / 180;
        const x1 = center + (radius + 10) * Math.cos(rad);
        const y1 = center + (radius + 10) * Math.sin(rad);
        const x2 = center + (radius + 15) * Math.cos(rad);
        const y2 = center + (radius + 15) * Math.sin(rad);
        
        ctx.strokeStyle = '#2d3748';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
    }
}

// Obtener color del gradiente
function getGradientColor(ratio) {
    if (ratio < 0.25) return '#ff6b35';
    if (ratio < 0.5) return '#f7931e';
    if (ratio < 0.75) return '#ffd700';
    return '#00f5ff';
}

// Animar anillo de progreso
function animateProgressRing(targetPercentage) {
    let current = appState.stats.percentage;
    const target = Math.min(100, Math.max(0, targetPercentage));
    const duration = 1000;
    const steps = 50;
    const stepDuration = duration / steps;
    const increment = (target - current) / steps;
    
    let step = 0;
    const interval = setInterval(() => {
        if (step >= steps) {
            clearInterval(interval);
            appState.stats.percentage = target;
            drawProgressRing(target);
            return;
        }
        
        current += increment;
        drawProgressRing(current);
        step++;
    }, stepDuration);
}

// Configurar event listeners
function setupEventListeners() {
    // Botones de selección
    document.getElementById('btnImage').addEventListener('click', () => {
        if (!appState.isProcessing) {
            document.getElementById('fileInput').click();
        }
    });
    
    document.getElementById('btnFolder').addEventListener('click', () => {
        if (!appState.isProcessing) {
            document.getElementById('folderInput').click();
        }
    });
    
    document.getElementById('btnOutput').addEventListener('click', () => {
        if (!appState.isProcessing) {
            showOutputInfo();
        }
    });
    
    // Inputs de archivo
    document.getElementById('fileInput').addEventListener('change', handleFileSelect);
    document.getElementById('folderInput').addEventListener('change', handleFolderSelect);
    
    // Slider de calidad
    const qualitySlider = document.getElementById('qualitySlider');
    qualitySlider.addEventListener('input', (e) => {
        updateQuality(e.target.value);
    });
    
    // Checkbox metadata
    document.getElementById('preserveMetadata').addEventListener('change', (e) => {
        appState.preserveMetadata = e.target.checked;
        saveSettings();
    });
    
    // Botón optimizar
    document.getElementById('btnOptimize').addEventListener('click', optimizeImages);
    
    // Guardar configuración al cerrar
    window.addEventListener('beforeunload', saveSettings);
}

// Mostrar información sobre destino de salida
function showOutputInfo() {
    alert('ℹ️ INFORMACIÓN SOBRE DESCARGA\n\n' +
          'En la versión web, las imágenes optimizadas se descargan automáticamente a tu carpeta de Descargas del navegador.\n\n' +
          'Las imágenes tendrán el prefijo "optimized_" en su nombre.\n\n' +
          '💡 Si prefieres seleccionar una carpeta específica, puedes:\n' +
          '1. Cambiar la ubicación de descarga en la configuración de tu navegador\n' +
          '2. Usar la versión desktop de ThermiReduce que permite seleccionar carpetas personalizadas');
}

// Manejar selección de archivo
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
        appState.selectedFiles = files;
        document.getElementById('selectedPath').textContent = files[0].name;
        resetResults();
    }
}

// Manejar selección de carpeta
function handleFolderSelect(e) {
    const files = Array.from(e.target.files).filter(file => 
        /\.(jpg|jpeg|png|webp|bmp)$/i.test(file.name)
    );
    if (files.length > 0) {
        appState.selectedFiles = files;
        document.getElementById('selectedPath').textContent = 
            `${files.length} archivo(s) seleccionado(s)`;
        resetResults();
    }
}

// Actualizar calidad
function updateQuality(value) {
    appState.quality = parseInt(value);
    const display = document.getElementById('qualityDisplay');
    display.textContent = `${value}%`;
    
    if (value < 70) {
        display.style.color = '#ff6b35';
    } else if (value < 85) {
        display.style.color = '#f7931e';
    } else {
        display.style.color = '#00ff88';
    }
    
    saveSettings();
}

// Resetear resultados
function resetResults() {
    appState.stats = {
        originalSize: 0,
        optimizedSize: 0,
        savedSize: 0,
        filesCount: 0,
        percentage: 0
    };
    
    updateStatsDisplay();
    drawProgressRing(0);
    document.getElementById('currentFile').textContent = 'Esperando...';
}

// Actualizar display de estadísticas
function updateStatsDisplay() {
    const [origVal, origUnit] = formatSize(appState.stats.originalSize);
    const [optVal, optUnit] = formatSize(appState.stats.optimizedSize);
    const [savedVal, savedUnit] = formatSize(appState.stats.savedSize);
    
    document.getElementById('originalSize').textContent = origVal;
    document.getElementById('originalUnit').textContent = origUnit;
    document.getElementById('optimizedSize').textContent = optVal;
    document.getElementById('optimizedUnit').textContent = optUnit;
    document.getElementById('savedSize').textContent = savedVal;
    document.getElementById('savedUnit').textContent = savedUnit;
    document.getElementById('filesCount').textContent = appState.stats.filesCount;
}

// Formatear tamaño
function formatSize(bytes) {
    if (bytes < 1024) return [bytes.toFixed(2), 'B'];
    if (bytes < 1024 * 1024) return [(bytes / 1024).toFixed(2), 'KB'];
    if (bytes < 1024 * 1024 * 1024) return [(bytes / (1024 * 1024)).toFixed(2), 'MB'];
    return [(bytes / (1024 * 1024 * 1024)).toFixed(2), 'GB'];
}

// Optimizar imágenes
async function optimizeImages() {
    if (appState.selectedFiles.length === 0) {
        alert('Por favor selecciona una imagen o carpeta primero');
        return;
    }
    
    if (appState.isProcessing) return;
    
    setProcessingState(true);
    animateProgressBar();
    
    let totalOriginal = 0;
    let totalOptimized = 0;
    let processedCount = 0;
    
    try {
        for (let i = 0; i < appState.selectedFiles.length; i++) {
            const file = appState.selectedFiles[i];
            
            // Actualizar UI
            document.getElementById('currentFile').textContent = file.name;
            
            // Obtener tamaño original
            totalOriginal += file.size;
            
            // Comprimir imagen
            const compressed = await compressImage(file, appState.quality);
            totalOptimized += compressed.size;
            processedCount++;
            
            // Actualizar contador
            appState.stats.filesCount = processedCount;
            document.getElementById('filesCount').textContent = processedCount;
            
            // Descargar imagen comprimida
            downloadImage(compressed, file.name);
            
            // Pequeña pausa para no sobrecargar
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        // Calcular estadísticas finales
        const saved = totalOriginal - totalOptimized;
        const percentage = totalOriginal > 0 ? (saved / totalOriginal * 100) : 0;
        
        appState.stats.originalSize = totalOriginal;
        appState.stats.optimizedSize = totalOptimized;
        appState.stats.savedSize = saved;
        
        updateStatsDisplay();
        animateProgressRing(percentage);
        
        // Mensaje de éxito
        setTimeout(() => {
            alert(`✓ Proceso completado exitosamente\n\n` +
                  `► ${processedCount} de ${appState.selectedFiles.length} imagen(es) procesada(s)\n` +
                  `► Reducción total: ${percentage.toFixed(1)}%\n` +
                  `► Espacio ahorrado: ${formatSize(saved)[0]} ${formatSize(saved)[1]}`);
        }, 500);
        
    } catch (error) {
        alert(`Error durante la optimización:\n\n${error.message}`);
    } finally {
        setProcessingState(false);
        document.getElementById('currentFile').textContent = 'Completado';
    }
}

// Comprimir imagen
function compressImage(file, quality) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const img = new Image();
            
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                
                canvas.toBlob((blob) => {
                    if (blob) {
                        const newFile = new File([blob], file.name, {
                            type: 'image/jpeg',
                            lastModified: Date.now()
                        });
                        resolve(newFile);
                    } else {
                        reject(new Error('Error al comprimir la imagen'));
                    }
                }, 'image/jpeg', quality / 100);
            };
            
            img.onerror = () => reject(new Error('Error al cargar la imagen'));
            img.src = e.target.result;
        };
        
        reader.onerror = () => reject(new Error('Error al leer el archivo'));
        reader.readAsDataURL(file);
    });
}

// Descargar imagen
function downloadImage(file, originalName) {
    const url = URL.createObjectURL(file);
    const a = document.createElement('a');
    a.href = url;
    
    // Cambiar extensión a .jpg si era PNG, WebP o BMP
    let fileName = originalName;
    if (/\.(png|webp|bmp)$/i.test(originalName)) {
        fileName = originalName.replace(/\.(png|webp|bmp)$/i, '.jpg');
    }
    a.download = `optimized_${fileName}`;
    
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Establecer estado de procesamiento
function setProcessingState(processing) {
    appState.isProcessing = processing;
    
    const buttons = [
        document.getElementById('btnImage'),
        document.getElementById('btnFolder'),
        document.getElementById('btnOutput'),
        document.getElementById('btnOptimize')
    ];
    
    buttons.forEach(btn => {
        btn.disabled = processing;
    });
}

// Animar barra de progreso
function animateProgressBar() {
    const progressBar = document.getElementById('progressBar');
    let width = 0;
    const duration = 2000;
    const steps = 50;
    const increment = 100 / steps;
    const stepDuration = duration / steps;
    
    const interval = setInterval(() => {
        if (width >= 100 || !appState.isProcessing) {
            clearInterval(interval);
            progressBar.style.width = '100%';
            setTimeout(() => {
                progressBar.style.width = '0%';
            }, 300);
            return;
        }
        
        width += increment;
        progressBar.style.width = `${width}%`;
    }, stepDuration);
}

// Cargar configuración
function loadSettings() {
    try {
        const saved = JSON.parse(localStorage.getItem('thermireduce_config') || '{}');
        
        if (saved.quality) {
            appState.quality = saved.quality;
            document.getElementById('qualitySlider').value = saved.quality;
            updateQuality(saved.quality);
        }
        
        if (saved.preserveMetadata !== undefined) {
            appState.preserveMetadata = saved.preserveMetadata;
            document.getElementById('preserveMetadata').checked = saved.preserveMetadata;
        }
    } catch (error) {
        console.error('Error al cargar configuración:', error);
    }
}

// Guardar configuración
function saveSettings() {
    try {
        const config = {
            quality: appState.quality,
            preserveMetadata: appState.preserveMetadata
        };
        localStorage.setItem('thermireduce_config', JSON.stringify(config));
    } catch (error) {
        console.error('Error al guardar configuración:', error);
    }
}