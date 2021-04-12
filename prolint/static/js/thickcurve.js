function thickcurve(id) {

    dir = "/media/user-data/" + username + "/" + task_id + "/";

    if (WEBGL.isWebGLAvailable() === false) {
        document.body.appendChild(WEBGL.getWebGLErrorMessage());
    }

    var container, controls, camera, scene, renderer;

    init();
    animate();

    function init() {
        var allPromises = [];
        var clientHeight = document.getElementById('thickcurve').clientHeight;
        var clientWidth = document.getElementById('thickcurve').clientWidth;


        container = document.getElementById('thickcurve');

        camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 200000);

        camera.zoom = 2.5
        camera.position.set(18.37, 19.82, 100.54);
        camera.lookAt(0, 3, 1);
        camera.updateProjectionMatrix()

        renderer = new THREE.WebGLRenderer({
            antialias: true
        });

        scene = new THREE.Scene();
        scene.background = new THREE.Color('#ffffff');

        var sprite = new THREE.TextureLoader().load('/static/images/ball.png')

        var loader = new THREE.PLYLoader();
        allPromises.push(new Promise(function (resolve, reject) {

            loader.load(dir + 'top_plane_curv.ply', function (g) {

                col = g.attributes.color.array;
                vert = g.attributes.position.array;

                var geometry = new THREE.BufferGeometry();

                geometry.addAttribute('position', new THREE.Float32BufferAttribute(vert, 3));
                geometry.addAttribute('color', new THREE.Float32BufferAttribute(col, 3));

                var material = new THREE.PointsMaterial({
                    size: 1.5,
                    clipShadows: true,
                    vertexColors: THREE.VertexColors,
                    map: sprite,
                    alphaTest: 0.5,
                    transparent: false
                });
                // material.color.set('#cd2121')

                geometry.computeFaceNormals();
                geometry.computeVertexNormals();

                // geometry.computeBoundingSphere();

                particles = new THREE.Points(geometry, material);
                particles.name = 'topPoints';
                scene.add(particles);

                resolve(particles);
                reject("Could not load file.")
            });
        }));

        allPromises.push(new Promise(function (resolve, reject) {
            loader.load(dir + 'down_plane_curv.ply', function (g) {

                col = g.attributes.color.array;
                vert = g.attributes.position.array;

                var geometry = new THREE.BufferGeometry();

                geometry.addAttribute('position', new THREE.Float32BufferAttribute(vert, 3));
                geometry.addAttribute('color', new THREE.Float32BufferAttribute(col, 3));

                var material = new THREE.PointsMaterial({
                    size: 1.5,
                    clipShadows: true,
                    vertexColors: THREE.VertexColors,
                    map: sprite,
                    alphaTest: 0.5,
                    transparent: false
                });
                // material.color.set('#cd2121')

                geometry.computeFaceNormals();
                geometry.computeVertexNormals();

                // geometry.computeBoundingSphere();

                particles = new THREE.Points(geometry, material);
                particles.name = 'downPoints';
                scene.add(particles);

                resolve(particles);
                reject("Could not load file.")
            });
        }));

        allPromises.push(new Promise(function (resolve, reject) {
            loader.load(dir + 'mid_plane_curv.ply', function (g) {

                col = g.attributes.color.array;
                vert = g.attributes.position.array;

                var geometry = new THREE.BufferGeometry();

                geometry.addAttribute('position', new THREE.Float32BufferAttribute(vert, 3));
                geometry.addAttribute('color', new THREE.Float32BufferAttribute(col, 3));

                var material = new THREE.PointsMaterial({
                    size: 1.5,
                    clipShadows: true,
                    vertexColors: THREE.VertexColors,
                    map: sprite,
                    alphaTest: 0.5,
                    transparent: false
                });
                // material.color.set('#cd2121')

                geometry.computeFaceNormals();
                geometry.computeVertexNormals();

                // geometry.computeBoundingSphere();

                particles = new THREE.Points(geometry, material);
                particles.name = 'midPoints';
                scene.add(particles);

                resolve(particles);
                reject("Could not load file.")
            });
        }));



        loader.load(dir + 'prots.ply', function (g) {

            var geometry = new THREE.BufferGeometry();

            var positions = [];
            var lut = new THREE.Lut("blackbody", parseInt((g.attributes.position.count / 4)));
            var colors = [];
            var color = new THREE.Color();

            arr = 0
            col = 0
            for (i = 0; i < g.attributes.position.count; i++) {

                if (col >= ((g.attributes.position.count / 4))) {
                    col = 0
                }

                // populate positions
                x = g.attributes.position.array[arr + 0]
                y = g.attributes.position.array[arr + 1]
                z = g.attributes.position.array[arr + 2]
                positions.push(x, y, z);

                // populate colors
                color.setRGB(lut.lut[col].r, lut.lut[col].b, lut.lut[col].g);
                colors.push(color.r, color.g, color.b);

                // increments
                arr = arr + 3
                col = col + 1

            }


            geometry.addAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
            geometry.addAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

            var material = new THREE.PointsMaterial({
                size: 2,
                vertexColors: THREE.VertexColors,
                map: sprite,
                alphaTest: 0.5,
                transparent: false
            });

            geometry.computeBoundingSphere();

            points = new THREE.Points(geometry, material);
            points.name = "pPoints"
            scene.add(points);

        });


        loader.load(dir + 'centers.ply', function (g) {

            var geometry = new THREE.BufferGeometry();

            var positions = [];
            var colors = [];
            var color = new THREE.Color();


            arr = 0
            for (i = 0; i < g.attributes.position.count; i++) {

                // populate positions
                x = g.attributes.position.array[arr + 0]
                y = g.attributes.position.array[arr + 1]
                z = g.attributes.position.array[arr + 2]
                positions.push(x, y, z);

                // populate colors
                color.setRGB(255, 255, 255);
                colors.push(color.r, color.g, color.b);

                // increments
                arr = arr + 3
            }


            geometry.addAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
            geometry.addAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

            var material = new THREE.PointsMaterial({
                size: 1.5,
                clipShadows: true,
                map: sprite,
                alphaTest: 0.5,
                transparent: false
            });
            // material.envMap = envMap;
            geometry.computeBoundingSphere();

            points2 = new THREE.Points(geometry, material);
            points2.name = "cPoints";
            scene.add(points2);

        });

        allPromises.push(new Promise(function (resolve, reject) {
            loader.load(dir + 'top_plane_curv.ply', function (geometry) {

                var material = new THREE.MeshStandardMaterial({
                    vertexColors: THREE.VertexColors,
                    roughness: 0,
                });
                var mesh = new THREE.Mesh(geometry, material);
                mesh.material.side = THREE.DoubleSide;
                mesh.name = "topCurve";

                scene.add(mesh);
                resolve(mesh);
                reject("Could not load file.")

            });
        }));



        allPromises.push(new Promise(function (resolve, reject) {
            loader.load(dir + 'top_plane_curv_g.ply', function (geometry) {

                var material = new THREE.MeshStandardMaterial({
                    vertexColors: THREE.VertexColors,
                    roughness: 0
                });
                var mesh = new THREE.Mesh(geometry, material);
                mesh.material.side = THREE.DoubleSide;
                mesh.name = "topCurveg";
                mesh.visible = false;

                scene.add(mesh);
                resolve(mesh);
                reject("Could not load file.")

            });
        }));

        allPromises.push(new Promise(function (resolve, reject) {
            loader.load(dir + 'top_thickness.ply', function (geometry) {

                var material = new THREE.MeshStandardMaterial({
                    vertexColors: THREE.VertexColors,
                    roughness: 0
                });
                var mesh = new THREE.Mesh(geometry, material);
                mesh.material.side = THREE.DoubleSide;
                mesh.name = "topThick";
                mesh.visible = false;

                scene.add(mesh);
                resolve(mesh);
                reject("Could not load file.")

            });
        }));

        allPromises.push(new Promise(function (resolve, reject) {
            loader.load(dir + 'down_plane_curv.ply', function (geometry) {

                var material = new THREE.MeshStandardMaterial({
                    vertexColors: THREE.VertexColors,
                    roughness: 0
                });
                var mesh = new THREE.Mesh(geometry, material);
                mesh.material.side = THREE.DoubleSide;
                mesh.name = "downCurve";

                scene.add(mesh);
                resolve(mesh);
                reject("Could not load file.")

            });
        }));

        allPromises.push(new Promise(function (resolve, reject) {
            loader.load(dir + 'down_plane_curv_g.ply', function (geometry) {

                var material = new THREE.MeshStandardMaterial({
                    vertexColors: THREE.VertexColors,
                    roughness: 0
                });
                var mesh = new THREE.Mesh(geometry, material);
                mesh.material.side = THREE.DoubleSide;
                mesh.name = "downCurveg";
                mesh.visible = false;

                scene.add(mesh);
                resolve(mesh);
                reject("Could not load file.")

            });
        }));

        allPromises.push(new Promise(function (resolve, reject) {
            loader.load(dir + 'down_thickness.ply', function (geometry) {

                var material = new THREE.MeshStandardMaterial({
                    vertexColors: THREE.VertexColors,
                    roughness: 0
                });
                var mesh = new THREE.Mesh(geometry, material);
                mesh.material.side = THREE.DoubleSide;
                mesh.name = "downThick";
                mesh.visible = false;

                scene.add(mesh);
                resolve(mesh);
                reject("Could not load file.")

            });
        }));


        allPromises.push(new Promise(function (resolve, reject) {
            loader.load(dir + 'mid_plane_curv.ply', function (geometry) {

                var material = new THREE.MeshStandardMaterial({
                    vertexColors: THREE.VertexColors,
                    roughness: 0
                });
                var mesh = new THREE.Mesh(geometry, material);
                mesh.material.side = THREE.DoubleSide;
                mesh.name = "midCurve";

                scene.add(mesh);
                resolve(mesh);
                reject("Could not load file.")

            });
        }));

        allPromises.push(new Promise(function (resolve, reject) {
            loader.load(dir + 'mid_plane_curv_g.ply', function (geometry) {

                var material = new THREE.MeshStandardMaterial({
                    vertexColors: THREE.VertexColors,
                    roughness: 0
                });
                var mesh = new THREE.Mesh(geometry, material);
                mesh.material.side = THREE.DoubleSide;
                mesh.name = "midCurveg";
                mesh.visible = false;

                scene.add(mesh);
                resolve(mesh);
                reject("Could not load file.")

            });
        }));

        allPromises.push(new Promise(function (resolve, reject) {
            loader.load(dir + 'full_thickness.ply', function (geometry) {

                var material = new THREE.MeshStandardMaterial({
                    vertexColors: THREE.VertexColors,
                    roughness: 0
                });
                var mesh = new THREE.Mesh(geometry, material);
                mesh.material.side = THREE.DoubleSide;
                mesh.name = "midThick";
                mesh.visible = false;

                scene.add(mesh);
                resolve(mesh);
                reject("Could not load file.")

            });
        }));

        var ambientLight = new THREE.AmbientLight(0x333333, 5);
        scene.add(ambientLight);

        var directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(0, 1, 0) //.normalize();
        scene.add(directionalLight);

        // renderer
        renderer = new THREE.WebGLRenderer();
        // renderer.setSize(500, 500);
        renderer.gammaInput = true;
        renderer.gammaOutput = true;
        // renderer.setPixelRatio( window.devicePixelRatio );
        renderer.setSize(clientWidth, clientHeight);
        container.appendChild(renderer.domElement);

        // controls
        controls = new THREE.TrackballControls(camera, renderer.domElement);
        controls.rotateSpeed = 10;
        controls.panSpeed = 1;
        controls.staticMoving = true;
        controls.zoomSpeed = 5;
        controls.target.set(10, 18, 0);

        function componentToHex(c) {
            var hex = c.toString(16);
            return hex.length == 1 ? "0" + hex : hex;
        }

        function rgbToHex(r, g, b) {
            return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
        }

        Promise.all(allPromises)
            .then(function (t) {

                var gui = new dat.GUI({
                    width: 240,
                    autoPlace: false
                });
                gui.domElement.id = 'gui';


                gui.open();

                var topPoints = scene.getObjectByName('topPoints');
                var midPoints = scene.getObjectByName('midPoints');
                var downPoints = scene.getObjectByName('downPoints');

                var topCurve = scene.getObjectByName('topCurve');
                var midCurve = scene.getObjectByName('midCurve');
                var downCurve = scene.getObjectByName('downCurve');

                var topCurveg = scene.getObjectByName('topCurveg');
                var midCurveg = scene.getObjectByName('midCurveg');
                var downCurveg = scene.getObjectByName('downCurveg');

                var topThick = scene.getObjectByName('topThick');
                var midThick = scene.getObjectByName('midThick');
                var downThick = scene.getObjectByName('downThick');

                var pPoints = scene.getObjectByName('pPoints');
                var cPoints = scene.getObjectByName('cPoints');

                curve_visible = {
                    "top_m": true,
                    "top_g": false,
                    "mid_m": true,
                    "mid_g": false,
                    "down_m": true,
                    "down_g": false,
                    "curve_state": 0
                }

                var size_dict = {
                    topPoints: 10,
                    midPoints: 10,
                    downPoints: 10,
                }

                var point_obj_dict = {
                    0: topPoints,
                    1: midPoints,
                    2: downPoints,
                }

                var mesh_obj_dict = {
                    0: topCurve,
                    1: midCurve,
                    2: downCurve
                }

                var point_dict = {
                    0: true,
                    1: false,
                    2: false,
                }

                var mesh_dict = {
                    0: true,
                    1: false,
                    2: false
                }


                param = {
                    motion: true,
                    'ambient intensity': ambientLight.intensity,
                    'saturation': 0.01,
                    'lightness': 1.0,
                    'directional light': 1.0,
                    "protein size": 2,
                    "surface type": 0,
                    'wireframe': false,
                    'envMapIntensity': 0,
                    'skybox': false,
                }

                mesh_param = {
                    "modify mesh": 0,
                    "roughness": 0,
                    "metalness": 0.1,
                    "wireframe": false,
                }

                point_param = {
                    "modify pointcloud": 0,
                    "point size": 10,
                }

                visi_param = {
                    "top points": true,
                    "top plane": true,
                    "mid points": true,
                    "mid plane": true,
                    "down points": true,
                    "down plane": true,
                    "protein points": true,
                    "lipid center points": true
                }

                var globalParams = gui.addFolder('Global Parameters');

                globalParams.add(param, 'ambient intensity', 0, 10).step(0.01).onChange(function (val) {
                    ambientLight.intensity = val;
                });

                globalParams.add(param, 'directional light', 0, 10).step(0.01).onChange(function (val) {
                    directionalLight.intensity = val;
                });

                globalParams.add(param, 'protein size', 0, 5).step(0.01).onChange(function (val) {
                    pPoints.material.size = val;
                });



                var meshParams = gui.addFolder('Mesh Properties');

                meshParams.add(param, 'surface type', {
                    "mean": 0,
                    "gaussian": 1,
                    "thickness": 2
                }).onChange(function (val) {
                    if (val == 0) {
                        console.log(topCurveg.visible)
                        console.log(topCurveg.visible | topThick.visible)
                        topCurve.visible = topCurveg.visible || topThick.visible
                        topCurveg.visible = false
                        topThick.visible = false
                        midCurve.visible = midCurveg.visible || midThick.visible
                        midCurveg.visible = false
                        midThick.visible = false
                        downCurve.visible = downCurveg.visible || downThick.visible
                        downCurveg.visible = false
                        downThick.visible = false
                    } else if (val == 1) {
                        topCurveg.visible = topCurve.visible || topThick.visible
                        topCurve.visible = false
                        topThick.visible = false
                        midCurveg.visible = midCurve.visible || midThick.visible
                        midCurve.visible = false
                        midThick.visible = false
                        downCurveg.visible = downCurve.visible || downThick.visible
                        downCurve.visible = false
                        downThick.visible = false
                    } else if (val == 2) {
                        topThick.visible = topCurveg.visible || topCurve.visible
                        topCurve.visible = false
                        topCurveg.visible = false
                        midThick.visible = midCurve.visible || midCurveg.visible
                        midCurve.visible = false
                        midCurveg.visible = false
                        downThick.visible = downCurve.visible || downCurveg.visible
                        downCurve.visible = false
                        downCurveg.visible = false

                    }

                    if (val == 0) {
                        curve_visible["curve_state"] = 0;
                    } else if (val == 1) {
                        curve_visible["curve_state"] = 1;
                    } else if (val == 2) {
                        curve_visible["curve_state"] = 2;
                    }
                })

                meshParams.add(mesh_param, "modify mesh", {
                    "top plane": 0,
                    "mid plane": 1,
                    "down plane": 2
                }).onChange(function (val) {
                    for (m in mesh_dict) {
                        mesh_dict[m] = false;
                    }
                    mesh_dict[val] = true;
                })

                meshParams.add(mesh_param, "metalness", 0, 1.0).step(0.01).onChange(function (val) {
                    for (m in mesh_dict) {
                        if (mesh_dict[m]) {
                            mesh_obj_dict[m].material.metalness = val;
                        }
                    }
                })

                meshParams.add(mesh_param, "roughness", 0, 1.0).step(0.01).onChange(function (val) {
                    for (m in mesh_dict) {
                        if (mesh_dict[m]) {
                            mesh_obj_dict[m].material.roughness = val;
                        }
                    }
                })

                meshParams.add(param, 'wireframe').onChange(function (val) {
                    topCurve.material.wireframe = val;
                    topCurveg.material.wireframe = val;
                    midCurve.material.wireframe = val;
                    midCurveg.material.wireframe = val;
                    downCurve.material.wireframe = val;
                    downCurveg.material.wireframe = val;
                    topThick.material.wireframe = val;
                    midThick.material.wireframe = val;
                    downThick.material.wireframe = val;
                })
                meshParams.open();

                var pointParams = gui.addFolder('Point Properties');
                pointParams.add(point_param, 'modify pointcloud', {
                    "top points": 0,
                    "mid points": 1,
                    "down points": 2,
                }).onChange(function (val) {

                    for (p in point_dict) {
                        point_dict[p] = false;
                    }
                    point_dict[val] = true;

                    for (var i = 0; i < pointParams.__controllers.length; i++) {
                        if (pointParams.__controllers[i].property == "color") {
                            for (p in point_dict) {
                                if (point_dict[p]) {
                                    color = point_obj_dict[p].material.color;
                                    hex = rgbToHex(color.r * 255, color.g * 255, color.b * 255);
                                    pointParams.__controllers[i].setValue(hex);
                                }
                            }
                        }

                        if (pointParams.__controllers[i].property == "point size") {
                            for (p in point_dict) {
                                if (point_dict[p]) {
                                    size = point_obj_dict[p].material.size;
                                    pointParams.__controllers[i].setValue(size)
                                }
                            }
                        }
                    }
                })

                pointParams.add(point_param, 'point size', 1, 25).onChange(function (val) {
                    for (p in point_dict) {
                        if (point_dict[p]) {
                            point_obj_dict[p].material.size = val
                            size_dict[point_obj_dict[p]] = val
                        }
                    }
                });

                var conf = {
                    color: '#2f22ff'
                };
                pointParams.addColor(conf, 'color').onChange(function (val) {
                    for (p in point_dict) {
                        if (point_dict[p]) {
                            point_obj_dict[p].material.color.set(val);
                        }
                    }
                });
                pointParams.open()


                // toggle the visibility of components
                var toggleVisibility = gui.addFolder('Component Visibility');
                toggleVisibility.add(visi_param, 'top points').onChange(function (val) {
                    topPoints.visible = val
                });

                toggleVisibility.add(visi_param, 'top plane').onChange(function (val) {
                    if (curve_visible["curve_state"] == 0) {
                        topCurve.visible = val
                    } else if (curve_visible["curve_state"] == 1) {
                        topCurveg.visible = val
                    } else if (curve_visible["curve_state"] == 2) {
                        topThick.visible = val
                    }
                });

                toggleVisibility.add(visi_param, 'mid points').onChange(function (val) {
                    midPoints.visible = val
                });

                toggleVisibility.add(visi_param, 'mid plane').onChange(function (val) {
                    if (curve_visible["curve_state"] == 0) {
                        midCurve.visible = val
                    } else if (curve_visible["curve_state"] == 1) {
                        midCurveg.visible = val
                    } else if (curve_visible["curve_state"] == 2) {
                        midThick.visible = val
                    }
                });

                toggleVisibility.add(visi_param, 'down points').onChange(function (val) {
                    downPoints.visible = val
                });

                toggleVisibility.add(visi_param, 'down plane').onChange(function (val) {
                    if (curve_visible["curve_state"] == 0) {
                        downCurve.visible = val
                    } else if (curve_visible["curve_state"] == 1) {
                        downCurveg.visible = val
                    } else if (curve_visible["curve_state"] == 2) {
                        downThick.visible = val
                    }
                });

                toggleVisibility.add(visi_param, 'protein points').onChange(function (val) {
                    pPoints.visible = val
                });

                toggleVisibility.add(visi_param, 'lipid center points').onChange(function (val) {
                    cPoints.visible = val
                });

                guis['g'] = gui

                var guiContainer = document.getElementById('gui-container');
                guiContainer.appendChild(gui.domElement);

            }, function () {
                console.log("Could not load GUI correctly")
            });

        // listener
        window.addEventListener('resize', onWindowResize, false);

    }

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
    }

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        render();
    }

    function render() {
        renderer.render(scene, camera);
    }

    return scene
}