/**
 * 3D Letter Viewer
 * A ThreeJS-based component for rendering 3D letters with customizable materials and colors
 */

class LetterViewer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.letters = options.letters || 'LOGO';
        this.letterSpacing = options.letterSpacing || 0.2;
        this.fontName = options.fontName || 'Arial';
        this.height = options.height || 2;
        this.depth = options.depth || 0.5;
        this.material = options.material || 'plastic';
        this.finish = options.finish || 'Standard';
        this.multiColor = options.multiColor || false;
        this.color = options.color || '#3498db';
        this.letterColors = options.letterColors || {};
        this.backgroundColor = options.backgroundColor || '#f8f9fa';
        
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.letterObjects = [];
        this.fontsLoaded = false;
        this.isAnimating = true;
        
        this.materialOptions = {
            'plastic': {
                roughness: 0.7,
                metalness: 0.0,
                reflectivity: 0.2
            },
            'metal': {
                roughness: 0.2,
                metalness: 0.8,
                reflectivity: 0.8
            },
            'wood': {
                roughness: 0.9,
                metalness: 0.0,
                reflectivity: 0.1
            },
            'glass': {
                roughness: 0.0,
                metalness: 0.0,
                reflectivity: 1.0,
                transparent: true,
                opacity: 0.7
            },
            'acrylic': {
                roughness: 0.2,
                metalness: 0.0,
                reflectivity: 0.4,
                transparent: true,
                opacity: 0.8
            }
        };
        
        this.finishOptions = {
            'Standard': {},
            'Painted': {
                roughness: 0.5
            },
            'Chrome': {
                metalness: 0.9,
                roughness: 0.1
            },
            'Gold': {
                metalness: 0.8,
                roughness: 0.2,
                color: '#FFD700'
            },
            'Brushed': {
                roughness: 0.6,
                metalness: 0.6
            }
        };
        
        // Initialize the viewer
        this.init();
    }
    
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(this.backgroundColor);
        
        // Create camera
        const aspectRatio = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, aspectRatio, 0.1, 1000);
        this.camera.position.z = 10;
        
        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);
        
        // Add orbit controls
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.25;
        this.controls.enableZoom = true;
        
        // Add lights
        this.addLights();
        
        // Add floor/shadow catcher
        this.addFloor();
        
        // Load font and create letters
        this.loadFont();
        
        // Handle window resize
        window.addEventListener('resize', this.onWindowResize.bind(this), false);
        
        // Start animation loop
        this.animate();
    }
    
    loadFont(customFont = null) {
        const fontLoader = new THREE.FontLoader();
        const fontPath = customFont || 'https://threejs.org/examples/fonts/helvetiker_regular.typeface.json';
        
        fontLoader.load(fontPath, (font) => {
            this.font = font;
            this.fontsLoaded = true;
            this.createLetters();
        });
    }
    
    addLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);
        
        // Main directional light (with shadows)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 10, 7);
        directionalLight.castShadow = true;
        
        // Adjust shadow properties
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -10;
        directionalLight.shadow.camera.right = 10;
        directionalLight.shadow.camera.top = 10;
        directionalLight.shadow.camera.bottom = -10;
        
        this.scene.add(directionalLight);
        
        // Fill light
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
        fillLight.position.set(-5, 5, -5);
        this.scene.add(fillLight);
        
        // Back light
        const backLight = new THREE.DirectionalLight(0xffffff, 0.2);
        backLight.position.set(0, 5, -10);
        this.scene.add(backLight);
    }
    
    addFloor() {
        const floorGeometry = new THREE.PlaneGeometry(50, 50);
        const floorMaterial = new THREE.ShadowMaterial({ opacity: 0.2 });
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = -this.height / 2 - 0.01; // Slightly below the letters
        floor.receiveShadow = true;
        
        this.scene.add(floor);
    }
    
    createLetters() {
        if (!this.fontsLoaded) return;
        
        // Clear existing letters
        this.letterObjects.forEach(letter => this.scene.remove(letter));
        this.letterObjects = [];
        
        // Get letter geometries and total width
        const letterGeometries = [];
        let totalWidth = 0;
        
        for (let i = 0; i < this.letters.length; i++) {
            const char = this.letters[i];
            
            // Skip space characters but account for their width
            if (char === ' ') {
                totalWidth += this.height * 0.5;
                continue;
            }
            
            const geometry = new THREE.TextGeometry(char, {
                font: this.font,
                size: this.height,
                height: this.depth,
                curveSegments: 12,
                bevelEnabled: true,
                bevelThickness: 0.1,
                bevelSize: 0.05,
                bevelSegments: 5
            });
            
            geometry.computeBoundingBox();
            const letterWidth = geometry.boundingBox.max.x - geometry.boundingBox.min.x;
            
            letterGeometries.push({
                char: char,
                geometry: geometry,
                width: letterWidth
            });
            
            totalWidth += letterWidth + this.letterSpacing;
        }
        
        // Position letters
        let offsetX = -totalWidth / 2;
        
        for (let i = 0; i < letterGeometries.length; i++) {
            const letterData = letterGeometries[i];
            const material = this.createMaterial(letterData.char);
            
            const letter = new THREE.Mesh(letterData.geometry, material);
            letter.castShadow = true;
            letter.receiveShadow = true;
            
            letter.position.x = offsetX;
            this.scene.add(letter);
            this.letterObjects.push(letter);
            
            offsetX += letterData.width + this.letterSpacing;
        }
        
        // Center the group of letters
        this.centerCamera();
    }
    
    createMaterial(letter) {
        // Get base material properties
        const materialProps = { ...this.materialOptions[this.material] };
        
        // Apply finish properties
        if (this.finishOptions[this.finish]) {
            Object.assign(materialProps, this.finishOptions[this.finish]);
        }
        
        // Determine color
        let color;
        if (this.multiColor && this.letterColors[letter]) {
            color = this.letterColors[letter];
        } else if (this.finish === 'Gold') {
            color = materialProps.color || '#FFD700';
        } else {
            color = this.color;
        }
        
        materialProps.color = new THREE.Color(color);
        
        // Create appropriate material
        const material = new THREE.MeshStandardMaterial(materialProps);
        
        // Handle special materials
        if (this.material === 'metal' || this.finish === 'Chrome' || this.finish === 'Gold') {
            material.envMap = this.createEnvironmentMap();
        }
        
        return material;
    }
    
    createEnvironmentMap() {
        // Create a simple environment map (ideally would use a real HDR env map)
        const cubeRenderTarget = new THREE.WebGLCubeRenderTarget(256);
        const cubeCamera = new THREE.CubeCamera(0.1, 1000, cubeRenderTarget);
        
        // Simple environment
        const envScene = new THREE.Scene();
        envScene.background = new THREE.Color(0xf0f0f0);
        
        // Add some gradient and lighting to the environment
        const light1 = new THREE.DirectionalLight(0xffffff, 1);
        light1.position.set(1, 1, 1);
        envScene.add(light1);
        
        const light2 = new THREE.DirectionalLight(0xffffff, 0.5);
        light2.position.set(-1, -1, -1);
        envScene.add(light2);
        
        cubeCamera.update(this.renderer, envScene);
        
        return cubeRenderTarget.texture;
    }
    
    centerCamera() {
        // Calculate bounding box of all letters
        const box = new THREE.Box3();
        this.letterObjects.forEach(letter => box.expandByObject(letter));
        
        // Get center and size of bounding box
        const center = new THREE.Vector3();
        box.getCenter(center);
        
        const size = new THREE.Vector3();
        box.getSize(size);
        
        // Update camera position to frame the letters
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = this.camera.fov * (Math.PI / 180);
        let cameraZ = Math.abs(maxDim / Math.sin(fov / 2));
        
        // Add some margin
        cameraZ *= 1.2;
        
        // Set camera position and target
        this.camera.position.z = cameraZ;
        this.controls.target.copy(center);
        this.controls.update();
    }
    
    onWindowResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    animate() {
        if (!this.isAnimating) return;
        
        requestAnimationFrame(this.animate.bind(this));
        
        // Update controls
        this.controls.update();
        
        // Slowly rotate letters for showcase effect
        if (this.letterObjects.length > 0) {
            this.letterObjects.forEach(letter => {
                letter.rotation.y += 0.002;
            });
        }
        
        // Render scene
        this.renderer.render(this.scene, this.camera);
    }
    
    // Public methods for updating properties
    setLetters(text) {
        this.letters = text;
        this.createLetters();
    }
    
    setMaterial(material) {
        if (this.materialOptions[material]) {
            this.material = material;
            this.updateMaterials();
        }
    }
    
    setFinish(finish) {
        if (this.finishOptions[finish]) {
            this.finish = finish;
            this.updateMaterials();
        }
    }
    
    setColor(color) {
        this.color = color;
        this.updateMaterials();
    }
    
    setMultiColor(isMultiColor, letterColors = {}) {
        this.multiColor = isMultiColor;
        this.letterColors = letterColors;
        this.updateMaterials();
    }
    
    setDimensions(height, depth) {
        this.height = height;
        this.depth = depth;
        this.createLetters();
    }
    
    setFont(fontUrl) {
        this.loadFont(fontUrl);
    }
    
    updateMaterials() {
        if (this.letterObjects.length > 0) {
            for (let i = 0; i < this.letters.length; i++) {
                if (i < this.letterObjects.length) {
                    const letter = this.letterObjects[i];
                    letter.material = this.createMaterial(this.letters[i]);
                }
            }
        }
    }
    
    toggleAnimation(animate) {
        this.isAnimating = animate;
        if (animate) {
            this.animate();
        }
    }
    
    dispose() {
        // Clean up resources
        this.isAnimating = false;
        
        // Remove event listeners
        window.removeEventListener('resize', this.onWindowResize);
        
        // Dispose of geometries and materials
        this.letterObjects.forEach(letter => {
            letter.geometry.dispose();
            letter.material.dispose();
        });
        
        // Remove renderer
        if (this.renderer) {
            this.renderer.dispose();
            this.container.removeChild(this.renderer.domElement);
        }
    }
}