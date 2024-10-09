<template>
  <!--Container for the Three.js scene -->
  <div ref="sceneContainer" class="scene-container">
    <button class="view-all-button" @click="viewAll">Relocate</button>
    <Modal :visible="isModalVisible" @close="closeModal">
      <h1 style="color: black">Real-time Seismic Data</h1>
      <SeismicChart
        v-if="chartData && chartData.datasets && chartData.datasets.length"
        :chartData="chartData"
        :chartOptions="chartOptions"
      />
    </Modal>
    <Modal :visible="isLoadingModalVisible" @close="closeLoadingModal">
      <h1>Please note:</h1>
      <p>
        This project contains complex graphics and heavy resources, which may
        take a while to load correctly. We appreciate your patience while
        everything gets set up for the best experience.
      </p>
    </Modal>
  </div>
</template>

<script>
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import Modal from "./Modal.vue";
import SeismicChart from "./SeismicChart.vue";
import { io } from "socket.io-client";

export default {
  name: "CelestialScene",
  components: {
    Modal,
    SeismicChart,
  },
  data() {
    return {
      isModalVisible: false,
      isLoadingModalVisible: true,
      selectedSpaceship: null,
      marsSpaceships: [],
      moonSpaceships: [],
      marsTransmissionLines: [],
      moonTransmissionLines: [],
      allTransmissionLines: [],
      satelliteSelected: null,
      chartData: {
        labels: [],
        datasets: [],
      },
      chartOptions: {
          animation: false,
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            y: {
              ticks: {
                callback: function (value) {
                  return value.toExponential(2);
                }
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function (context) {
                  let label = context.dataset.label || '';
                  if (label) {
                    label += ': ';
                  }
                  label += context.raw.toExponential(2);
                  return label;
                }
              }
            },
            decimation: {
              enabled: true,
              algorithm: 'lttb',
              threshold: 400,
              samples: 800
            }
          }
      },
    };
  },
  computed: {
    spaceshipImage() {
      if (!this.selectedSpaceship) return "";
      if (this.selectedSpaceship.userData.body === "Mars") {
        return "https://img.freepik.com/foto-gratis/retrato-perro-feliz-mirando-adelante_1194-589013.jpg?size=626&ext=jpg&ga=GA1.1.1413502914.1719964800&semt=ais_user";
      } else if (this.selectedSpaceship.userData.body === "Moon") {
        return "https://img.freepik.com/foto-gratis/retrato-perro-feliz-mirando-adelante_1194-589013.jpg?size=626&ext=jpg&ga=GA1.1.1413502914.1719964800&semt=ais_user";
      } else {
        return "https://img.freepik.com/foto-gratis/retrato-perro-feliz-mirando-adelante_1194-589013.jpg?size=626&ext=jpg&ga=GA1.1.1413502914.1719964800&semt=ais_user";
      }
    },
  },
  mounted() {
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.raycaster = null;
    this.mouse = null;
    this.earthModel = null;
    this.marsModel = null;
    this.moonModel = null;
    this.spaceshipGeometry = null;
    this.spaceshipMaterial = null;
    this.satellitesData = Array.from({ length: 6 }, () => []);
    this.satelliteData = [];
    this.predictedArray = Array.from({ length: 6 }, () => null);
    this.socket = null;

    fetch("http://satellite:10000/v1/api/satellite/generate_data")
      .then((response) => response.json())

    this.initThreeJS();

    this.socket = io("http://back:10001");
    this.socket.on("connect", () => {
      console.log("Connected to server");
    });

    this.socket .on("prediction", (prediction) => {
      console.log("Prediction received:", prediction);
      this.SeismDetection(prediction);
    });

    this.socket.on("big_data", (data) => {
      this.satelliteData = data;
      console.log("Length of satellite data:", this.satelliteData.length);
      this.updateChartData(this.satelliteData);
    });

    this.socket.on("small_data", (data) => {
        this.satelliteData.push(...data);
      console.log("Length of satellite data:", this.satelliteData.length);
      this.updateChartData(this.satelliteData);
    });
  },
  watch: {
    charData: {
      handler: function (newData) {
        this.updateChartData(newData);
      },
      deep: true,
    },
  },
  methods: {
    initThreeJS() {
      this.scene = new THREE.Scene();

      this.camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
      );
      this.camera.position.set(15, 5, 20);

      // Renderer setup
      this.renderer = new THREE.WebGLRenderer({ antialias: true });
      this.renderer.setSize(window.innerWidth, window.innerHeight);
      this.$refs.sceneContainer.appendChild(this.renderer.domElement);

      // Controls setup
      this.controls = new OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.minDistance = 13;
      this.controls.maxDistance = 60;

      // Lighting
      const ambientLight = new THREE.AmbientLight(0xffffff, 1);
      this.scene.add(ambientLight);

      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
      directionalLight.position.set(0, 1, 0);
      this.scene.add(directionalLight);

      // Loaders
      const loader = new GLTFLoader();

      // Spaceship geometry and material
      this.spaceshipGeometry = new THREE.ConeGeometry(0.5, 1.5, 8);
      this.spaceshipMaterial = new THREE.MeshStandardMaterial({
        color: 0xff0000,
      });

      // Load Earth Model
      loader.load("/earth-3.glb", (gltf) => {
        this.earthModel = gltf.scene;
        this.earthModel.scale.set(4, 4, 4);
        this.earthModel.position.set(0, -8, 0);
        this.earthModel.name = "Earth";
        this.scene.add(this.earthModel);

        // Add point light to Earth
        const earthLight = new THREE.PointLight(0x4444ff, 1, 50);
        earthLight.position.set(0, -5, 0);
        this.scene.add(earthLight);
      });

      // Load Mars Model
      loader.load("/mars-2.glb", (gltf) => {
        this.marsModel = gltf.scene;
        this.marsModel.scale.set(1, 1, 1);
        this.marsModel.position.set(-10, 15, 0);
        this.marsModel.name = "Mars";
        this.scene.add(this.marsModel);

        // Add point light to Mars
        const marsLight = new THREE.PointLight(0xff0000, 0.5, 50);
        marsLight.position.copy(this.marsModel.position);
        this.scene.add(marsLight);

        // Create spaceships around Mars after it loads
        this.createSpaceshipsAroundBody(
          this.marsModel,
          this.marsSpaceships,
          this.marsTransmissionLines,
          5
        );
      });

      // Load Moon Model
      loader.load("moon-2.glb", (gltf) => {
        this.moonModel = gltf.scene;
        this.moonModel.scale.set(0.75, 0.75, 0.75);
        this.moonModel.position.set(0, 5, 0);
        this.moonModel.name = "Moon";
        this.scene.add(this.moonModel);

        // Add point light to Moon
        const moonLight = new THREE.PointLight(0xffffff, 0.5, 50);
        moonLight.position.copy(this.moonModel.position);
        this.scene.add(moonLight);

        // Create spaceships around Moon after it loads
        this.createSpaceshipsAroundBody(
          this.moonModel,
          this.moonSpaceships,
          this.moonTransmissionLines,
          3
        );
      });

      // Create starfield background
      this.createStarfield();

      // Initialize raycaster and mouse
      this.raycaster = new THREE.Raycaster();
      this.mouse = new THREE.Vector2();

      // Add event listener
      this.renderer.domElement.addEventListener("click", this.onClick, false);

      // Start animation
      this.animate();

      // Handle window resize
      window.addEventListener("resize", this.onWindowResize);
    },
    createStarfield() {
      const starsGeometry = new THREE.BufferGeometry();
      const loader = new THREE.TextureLoader();

      // Load the star texture
      loader.load("fotoEstrella.png", (texture) => {
        // Create material with the loaded texture
        const starsMaterial = new THREE.PointsMaterial({
          map: texture,
          size: 1.5,
          transparent: true,
        });

        const starVertices = [];

        // Generate random positions for the stars with a condition to prevent them being too close to planets
        for (let i = 0; i < 2000; i++) {
          let x, y, z;
          let tooClose;

          do {
            x = THREE.MathUtils.randFloatSpread(200);
            y = THREE.MathUtils.randFloatSpread(200);
            z = THREE.MathUtils.randFloatSpread(200);

            // Calculate distance from each planet
            const distanceToEarth = new THREE.Vector3(x, y, z).distanceTo(
              this.earthModel
                ? this.earthModel.position
                : new THREE.Vector3(0, -8, 0)
            );
            const distanceToMars = new THREE.Vector3(x, y, z).distanceTo(
              this.marsModel
                ? this.marsModel.position
                : new THREE.Vector3(-10, 15, 0)
            );
            const distanceToMoon = new THREE.Vector3(x, y, z).distanceTo(
              this.moonModel
                ? this.moonModel.position
                : new THREE.Vector3(0, 5, 0)
            );

            // Set a minimum distance to ensure stars are not too close to planets
            const minDistance = 50;
            tooClose =
              distanceToEarth < minDistance ||
              distanceToMars < minDistance ||
              distanceToMoon < minDistance;
          } while (tooClose);

          starVertices.push(x, y, z);
        }

        starsGeometry.setAttribute(
          "position",
          new THREE.Float32BufferAttribute(starVertices, 3)
        );

        // Create the points object with geometry and textured material
        const stars = new THREE.Points(starsGeometry, starsMaterial);
        this.scene.add(stars);
      });
    },
    createSpaceshipsAroundBody(
      body,
      spaceshipsArray,
      transmissionLinesArray,
      orbitRadius
    ) {
      const loader = new GLTFLoader();

      for (let i = 0; i < 3; i++) {
        const angle = (i / 3) * Math.PI * 2;

        // Initial position of the spaceship
        const x = body.position.x + orbitRadius * Math.cos(angle);
        const y = body.position.y + orbitRadius * Math.sin(angle) * 0.2;
        const z = body.position.z + orbitRadius * Math.sin(angle);

        // Load the satellite model
        loader.load("satellite.glb", (gltf) => {
          const spaceship = gltf.scene;
          spaceship.scale.set(0.2, 0.2, 0.2);
          spaceship.position.set(x, y, z);
          spaceship.rotation.x = Math.PI / 2;
          spaceship.userData.body = body.name;
          spaceship.userData.randomOffsetX = Math.random() * 2 - 1;
          spaceship.userData.randomOffsetY = Math.random() * 2 - 1;
          this.scene.add(spaceship);
          spaceshipsArray.push(spaceship);

          // Create the transmission line from planet to spaceship
          const transmissionLineToPlanet = this.createTransmissionLine(
            body.position.clone(),
            spaceship.position.clone(),
            {
              color: "#c2c2c2",
              opacity: 0.3,
              movingObjectColor: 0xffff00, // yellow
            }
          );
          transmissionLinesArray.push(transmissionLineToPlanet);
          this.allTransmissionLines.push(transmissionLineToPlanet); // Add to allTransmissionLines array

          // Create the transmission line from spaceship to Earth (initially invisible)
          const earthPosition = this.earthModel
            ? this.earthModel.position.clone()
            : new THREE.Vector3(0, -5, 0);
          const transmissionLineToEarth = this.createTransmissionLine(
            spaceship.position.clone(),
            earthPosition,
            {
              color: "#ff0000", // red line
              opacity: 1,
              movingObjectColor: 0xff0000, // red moving dot
            }
          );
          // Initially invisible
          transmissionLineToEarth.line.visible = false;
          transmissionLineToEarth.movingObject.visible = false;

          this.allTransmissionLines.push(transmissionLineToEarth);

          // Store the transmission lines in the spaceship's userData
          spaceship.userData.transmissionLines = {
            toPlanet: transmissionLineToPlanet,
            toEarth: transmissionLineToEarth,
          };

          // For simulating seism detection
          spaceship.userData.seismDetected = false;
        });
      }
    },
    createTransmissionLine(startPosition, endPosition, options) {
      // options: { color, opacity, movingObjectColor }

      const curve = this.createQuadraticCurve(startPosition, endPosition);

      // Create the line to visualize the curve
      const points = curve.getPoints(50);
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const material = new THREE.LineBasicMaterial({
        color: options.color || "#c2c2c2",
        transparent: true,
        opacity: options.opacity !== undefined ? options.opacity : 0.3,
      });
      const line = new THREE.Line(geometry, material);
      this.scene.add(line);

      // Create the moving object along the curve
      const movingObjectGeometry = new THREE.SphereGeometry(0.1, 8, 8);
      const movingObjectMaterial = new THREE.MeshBasicMaterial({
        color: options.movingObjectColor || 0xffff00,
      });
      const movingObject = new THREE.Mesh(
        movingObjectGeometry,
        movingObjectMaterial
      );
      movingObject.position.copy(startPosition);
      this.scene.add(movingObject);

      // Store the transmission line info
      const transmissionLine = {
        curve: curve,
        line: line,
        movingObject: movingObject,
        t: 0, // Parameter along the curve (0 to 1)
        startPosition: startPosition,
        endPosition: endPosition,
      };

      return transmissionLine;
    },
    createQuadraticCurve(startPosition, endPosition) {
      // Calculate the control point for the curve
      const controlPoint = startPosition
        .clone()
        .add(endPosition)
        .multiplyScalar(0.5);

      // Offset the control point to create a horizontal curve
      let dir = endPosition.clone().sub(startPosition);
      dir.y = 0;
      dir.normalize();

      let perpendicular = new THREE.Vector3(-dir.z, 0, dir.x);
      perpendicular.multiplyScalar(5); // Adjust the scalar to control the curvature
      controlPoint.add(perpendicular);

      // Create the curve
      const curve = new THREE.QuadraticBezierCurve3(
        startPosition,
        controlPoint,
        endPosition
      );
      return curve;
    },
    updateChartData(data) {
      if (!data || !Array.isArray(data) || !data.length) return;

      const times = data.map(tuple => Math.round(tuple[0]));
      const velocities = data.map(tuple => tuple[1]);

      let prediction = this.predictedArray[this.satelliteSelected];

      if (prediction && prediction[0]) {
        console.log("Prediction encountered:", prediction);
        let startTime = prediction[1];

        let startIndex = times.findIndex(time => time === Math.round(startTime));
        console.log("Start index:", startIndex);
        if (startIndex === -1) {
          let closestTime = times.reduce((prev, curr) => {
            return Math.abs(curr - startTime) < Math.abs(prev - startTime) ? curr : prev;
          });

          startIndex = times.findIndex(time => time === closestTime);
          console.log("Closest time:", closestTime);
        }

          let annotations = {
          line1: {
            type: "line",
            xMin: startIndex,
            xMax: startIndex,
            borderColor: "red",
            borderWidth: 2,
          },
        };
        this.chartData = {
          labels: times,
          datasets: [
            {
              label: "Velocities",
              data: velocities,
              fill: false,
              borderColor: "rgba(75, 192, 192, 1)",
              tension: 0.1,
            },
          ],
        };
        this.chartOptions = {
          animation: false,
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            y: {
              ticks: {
                callback: function (value) {
                  return value.toExponential(2);
                }
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function (context) {
                  let label = context.dataset.label || '';
                  if (label) {
                    label += ': ';
                  }
                  label += context.raw.toExponential(2); // Use 2 decimal places
                  return label;
                }
              }
            },
            decimation: {
              enabled: true,
              algorithm: 'lttb',
              threshold: 400,
              samples: 800
            },
            annotation: {
              annotations: annotations,
            },
          },
        };
      } else {
        this.chartData = {
          labels: times,
          datasets: [
            {
              label: "Velocities",
              data: velocities,
              fill: false,
              borderColor: "rgba(75, 192, 192, 1)",
              tension: 0.1,
            },
          ],
        };
        this.chartOptions = {
          animation: false,
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            y: {
              ticks: {
                callback: function (value) {
                  return value.toExponential(2);
                }
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function (context) {
                  let label = context.dataset.label || '';
                  if (label) {
                    label += ': ';
                  }
                  label += context.raw.toExponential(2); // Use 2 decimal places
                  return label;
                }
              }
            },
            decimation: {
              enabled: true,
              algorithm: 'lttb',
              threshold: 400,
              samples: 800
            }
          },
        };
      }
    },

    getColor(index) {
      const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];
      return colors[index % colors.length];
    },
    animate() {
      requestAnimationFrame(this.animate);

      // Rotate celestial bodies
      if (this.earthModel) this.earthModel.rotation.y += 0.0003;
      if (this.marsModel) this.marsModel.rotation.y += 0.001;
      if (this.moonModel) this.moonModel.rotation.y += 0.002;

      // Orbit spaceships
      const time = Date.now() * 0.00025;

      // Update Moon spaceships
      this.moonSpaceships.forEach((spaceship, i) => {
        const angle = time + (i / 3) * Math.PI * 2;
        const orbitRadius = 3;
        spaceship.position.x =
          this.moonModel.position.x +
          orbitRadius * Math.cos(angle) +
          Math.sin(time * 0.5 + spaceship.userData.randomOffsetX) * 0.5;
        spaceship.position.y =
          this.moonModel.position.y +
          orbitRadius * Math.sin(angle) * 0.2 +
          Math.cos(time * 0.5 + spaceship.userData.randomOffsetY) * 0.5;
        spaceship.position.z =
          this.moonModel.position.z +
          orbitRadius * Math.sin(angle) +
          Math.sin(time * 0.5 + spaceship.userData.randomOffsetX) * 0.5;
      });

      // Update Mars spaceships
      if (this.marsModel) {
        this.marsSpaceships.forEach((spaceship, i) => {
          const angle = time + (i / 3) * Math.PI * 2;
          const orbitRadius = 5;
          spaceship.position.x =
            this.marsModel.position.x +
            orbitRadius * Math.cos(angle) +
            Math.sin(time * 0.5 + spaceship.userData.randomOffsetX) * 0.5;
          spaceship.position.y =
            this.marsModel.position.y +
            orbitRadius * Math.sin(angle) * 0.2 +
            Math.cos(time * 0.5 + spaceship.userData.randomOffsetY) * 0.5;
          spaceship.position.z =
            this.marsModel.position.z +
            orbitRadius * Math.sin(angle) +
            Math.sin(time * 0.5 + spaceship.userData.randomOffsetX) * 0.5;
        });
      }

      const allSpaceships = this.marsSpaceships.concat(this.moonSpaceships);

      allSpaceships.forEach((spaceship) => {
        const bodyPosition =
          spaceship.userData.body === "Mars"
            ? this.marsModel.position
            : this.moonModel.position;

        // Update transmission line to planet
        const transmissionLineToPlanet =
          spaceship.userData.transmissionLines.toPlanet;
        this.updateTransmissionLine(
          transmissionLineToPlanet,
          bodyPosition,
          spaceship.position
        );

        // Update moving object along the line
        transmissionLineToPlanet.t += 0.005; // Adjust speed as necessary
        if (transmissionLineToPlanet.t > 1) transmissionLineToPlanet.t = 0; // Loop back
        const pointOnCurve = transmissionLineToPlanet.curve.getPoint(
          transmissionLineToPlanet.t
        );
        transmissionLineToPlanet.movingObject.position.copy(pointOnCurve);

        // If seism detected, update transmission line to Earth
        if (spaceship.userData.seismDetected) {
          const transmissionLineToEarth =
            spaceship.userData.transmissionLines.toEarth;
          this.updateTransmissionLine(
            transmissionLineToEarth,
            spaceship.position,
            this.earthModel.position
          );

          // Update moving object along the line
          transmissionLineToEarth.t += 0.004; // Adjust speed as necessary
          if (transmissionLineToEarth.t > 1) {
            transmissionLineToEarth.t = 0; // Reset t
            // Stop seism detection after one loop
            spaceship.userData.seismDetected = false;
            // Hide line to Earth
            transmissionLineToEarth.line.visible = false;
            transmissionLineToEarth.movingObject.visible = false;
          } else {
            const pointOnCurve = transmissionLineToEarth.curve.getPoint(
              transmissionLineToEarth.t
            );
            transmissionLineToEarth.movingObject.position.copy(pointOnCurve);
          }
        }
      });

      this.controls.update();
      this.renderer.render(this.scene, this.camera);
    },
    updateTransmissionLine(transmissionLine, startPosition, endPosition) {
      // Recalculate the curve
      const curve = this.createQuadraticCurve(startPosition, endPosition);
      transmissionLine.curve = curve;

      // Update the line geometry
      const points = curve.getPoints(50);
      transmissionLine.line.geometry.setFromPoints(points);
    },
    SeismDetection(predictionArray) {
      if (!predictionArray || predictionArray.length === 0) {
        console.error("No prediction data available");
        return;
      }

      // Combine all spaceships into one array
      const allSpaceships = this.marsSpaceships.concat(this.moonSpaceships);

      // Iterate over the prediction array
      /*
      predictionArray.forEach((object, index) => {
        if (object.prediction) {
          const spaceship = allSpaceships[index];
          spaceship.userData.seismDetected = true;
          spaceship.userData.transmissionLines.toEarth.t = 0; // Reset t
          if (this.predictedArray[index] === null) {
            //console.log("Prediction true for spaceship ", index);
            this.predictedArray[index] = object;
          }

          // Show line to Earth
          const transmissionLineToEarth =
            spaceship.userData.transmissionLines.toEarth;
          transmissionLineToEarth.line.visible = true;
          transmissionLineToEarth.movingObject.visible = true;

        }
      });
      */

      //predictionArray has this type [[false,-1],[false,-1],[true,68575.84905660378],[false,-1],[false,-1],[false,-1]]
      //Iterate over the prediction array
      predictionArray.forEach((object, index) => {
        if (object[0]) {
          const spaceship = allSpaceships[index];
          spaceship.userData.seismDetected = true;
          spaceship.userData.transmissionLines.toEarth.t = 0;
          if (this.predictedArray[index] === null) {
            this.predictedArray[index] = object;
            const transmissionLineToEarth =
            spaceship.userData.transmissionLines.toEarth;
          transmissionLineToEarth.line.visible = true;
          transmissionLineToEarth.movingObject.visible = true;
          }
        }
      });
    },
    onWindowResize() {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
    },
    onClick(event) {
      // Calculate mouse position in normalized device coordinates (-1 to +1)
      const rect = this.renderer.domElement.getBoundingClientRect();
      this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      // Update the raycaster
      this.raycaster.setFromCamera(this.mouse, this.camera);

      // Set a threshold for detecting intersections
      this.raycaster.params.Points.threshold = 0.5; // Example threshold (increase as needed)

      // Combine all spaceships into one array
      const allSpaceships = this.marsSpaceships.concat(this.moonSpaceships);

      // Check for intersections
      const intersects = this.raycaster.intersectObjects(allSpaceships, true);

      if (intersects.length > 0) {
        // A spaceship or part of a spaceship was clicked
        let clickedObject = intersects[0].object;

        // Traverse up to find the root object (spaceship)
        while (clickedObject.parent && !clickedObject.userData.body) {
          clickedObject = clickedObject.parent;
        }

        this.selectedSpaceship = clickedObject;
        //console.log("Spaceship clicked:", this.selectedSpaceship.index);
        //console.log("Los datos que le paso al chart son:", this.satellitesData[this.selectedSpaceship.index]);
        //this.updateChartData(this.satellitesData[this.selectedSpaceship.index]);
        this.openModal();

        // Find the index of the clicked spaceship in the combined array
        const spaceshipIndex = allSpaceships.findIndex(
          (spaceship) => spaceship.uuid === clickedObject.uuid
        );
        this.satelliteSelected = spaceshipIndex;

        // Log the clicked spaceship details to the console
        //console.log("Spaceship clicked!");
        //console.log("Spaceship Details:", {
        //  index: spaceshipIndex,
        //  position: clickedObject.position,
        //  id: clickedObject.uuid,
        //});
        //console.log("Los datos que le paso al chart son:", this.satellitesData[spaceshipIndex]);
        this.socket.emit("join", spaceshipIndex);
        //this.updateChartData(this.satellitesData[this.satelliteSelected]);
      } else {
        //console.log("No spaceship clicked.");
      }
    }
    ,
    openModal() {
      this.isModalVisible = true;
    },
    closeModal() {
      this.isModalVisible = false;
      this.socket.emit("join", -1);
      this.satelliteSelected = null;
      this.satelliteData = [];
    },
    closeLoadingModal() {
      this.isLoadingModalVisible = false;
    },
    viewAll() {
      // Adjust camera position to see everything
      const boundingBox = new THREE.Box3().setFromObject(this.scene);
      const center = boundingBox.getCenter(new THREE.Vector3());
      const size = boundingBox.getSize(new THREE.Vector3());

      const maxDim = Math.max(size.x, size.y, size.z);
      const fov = this.camera.fov * (Math.PI / 180);
      let cameraZ = Math.abs(maxDim / (2 * Math.tan(fov / 2)));

      cameraZ *= 0.23;
      this.camera.position.set(center.x, center.y + 15, cameraZ);
      this.camera.lookAt(center);

      // Update controls to ensure the camera points correctly
      this.controls.update();
    },
  },
  beforeDestroy() {
    // Clean up event listeners and Three.js resources
    window.removeEventListener("resize", this.onWindowResize);
    this.renderer.domElement.removeEventListener("click", this.onClick, false);
    // Additional cleanup if necessary
  },
};
</script>

<style>
.scene-container {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  position: absolute;
  top: 0;
  left: 0;
}

.view-all-button {
  position: absolute;
  top: 30px;
  right: 30px;
  padding: 10px;
  background-color: grey;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  z-index: 10;
  font-family: "Montserrat", sans-serif;
  font-size: 20px;
}

.view-all-button:hover {
  background-color: darkgrey;
}
</style>
