document.addEventListener("DOMContentLoaded", function () {
  stage = new NGL.Stage("gpcr-network");
  stage.mouseControls.remove("scroll-shift");

  stage.setParameters({
    backgroundColor: "white",
    cameraType: "orthographic",
    tooltip: false,
    clipDist: 0,
    lightIntensity: 1.13
  })

  function addElement(el) {
    Object.assign(el.style, {
      position: "relative",
    })
    document.getElementById('viewer-parent').prepend(el)
    // stage.viewer.container.prepend(el)
  }

  function createElement(name, properties, style) {
    var el = document.createElement(name)
    Object.assign(el, properties)
    Object.assign(el.style, style)
    return el
  }

  function createSelect(options, properties, style) {
    var select = createElement("select", properties, style)
    options.forEach(function (d) {
      select.add(createElement("option", {
        value: d[0],
        text: d[1]
      }))
    })
    return select
  }

  var scrollCHOL

  function isolevelScroll(stage, delta) {
    var d = Math.sign(delta) / 10
    stage.eachRepresentation(function (reprElem) {
      var p
      p = reprElem.getParameters()
      reprElem.setParameters({
        isolevel: Math.max(0.01, p.isolevel + d)
      })
    })
  }
  stage.mouseControls.add("scroll-shift", isolevelScroll)

  function loadStructure(input, name = "N/A", pdbID = "#") {
    struc = undefined
    surfCHOL = undefined
    labelPosition.value = 10
    toggleLabelButton.value = "Show Labels"
    isolevelCHOLText.innerText = ""
    stage.setFocus(0)
    stage.removeAllComponents()
    return stage.loadFile(input).then(function (o) {

      gpcrNameText.innerHTML = ''
      STATE = 2
      struc = o

      o.autoView()

      o.addRepresentation("cartoon", {
        radiusType: "size",
        colorScheme: "residueindex"
      })
      surface = o.addRepresentation("surface", {
        surfaceType: "av",
        probeRadius: 2.1,
        // sele: ".BB",
        opacity: 0.7,
        clipNear: 0
      })
      labels = o.addRepresentation("label", {
        labelType: "format",
        labelFormat: "%(resno)s%(resname)s",
        labelGrouping: "residue",
        fontWeight: "normal",
        radiusType: "bfactor",
        showBackground: true,
        backgroundColor: "red",
        backgroundOpacity: 100,
        zOffset: 10,
        color: "white",
      })
      labels.parameters.showL = showLabel(labels, 10);
      labels.toggleVisibility();

      var bf = Array.from(labels.parent.structure.atomStore.bfactor);
      var bfMax = Math.max.apply(null, bf);
      labels.setParameters({
        radiusScale: getBfMax(bfMax)
      })
    })
  }

  // Adjust the label size showing.
  function getBfMax(bfMax) {
    if (bfMax <= 20) {
      var radScale = 0.2;
    } else if (bfMax >= 20 && bfMax <= 30) {
      var radScale = 0.15;
    } else if (bfMax > 30 && bfMax <= 40) {
      var radScale = 0.1;
    } else if (bfMax > 40 && bfMax <= 50) {
      var radScale = 0.07;
    } else if (bfMax > 50) {
      var radScale = 0.07;
    }
    return radScale
  }

  // Selection to be parsed for showing labels based on bfactors.
  function showLabel(e, E) {
    var arr = Array.from(e.parent.structure.atomStore.bfactor)
    ARR = showAtom(arr, E);
    str = "";
    for (i = 0; i < ARR.length; i++) {
      str = str + ARR[i] + ", ";
    }
    if (str.length == 0) {
      e.setSelection(",");
    } else {
      e.setSelection(str);
    }
  }

  // Select only atoms that fit the bfactor cutoff.
  function showAtom(arr, E) {
    var ARR = []
    for (i = 0; i < arr.length; i++) {
      if (arr[i] < E) {
        continue
      } else {
        ARR.push(i + 1);
      }
    }
    return ARR
  }

  // Load the density file.
  var surfCHOL, sliceReprCHOL

  function loadCHOL(input, color_surface = "#f40f68") {
    return stage.loadFile(input).then(function (o) {
      isolevelCHOLText.innerText = "Lipid level: 2.0\u03C3"
      scrollCHOL = true
      surfCHOL = o.addRepresentation("surface", {
        color: "#" + color_surface,
        isolevel: 2.0,
        useWorker: true,
        contour: false,
        opaqueBack: false,
        isolevelScroll: false,
        opacity: 0.8
      })

      sliceReprCHOL = o.addRepresentation("slice", {
        dimension: "x",
        positionType: "percent",
        filter: "cubic-catmulrom",
      })
      sliceReprCHOL.toggleVisibility()
    })
  }

  lipid_select_list = []
  for (i = 0; i < task_result.length; i++) {
    lipid_select_list.push([task_result[i], task_result[i]])
  }

  var exampleSelect = createSelect(
    lipid_select_list, {
      id: "lipidSelect",
      onchange: function (e) {
        var id = e.target.value
        loadGPCR(id)
      }
    })
  addElement(exampleSelect)

  if (task_result.includes("CHOL")) {
    document.getElementById('lipidSelect').value = "CHOL";
  } else if (task_result.includes("PIP")) {
    document.getElementById('lipidSelect').value = "PIP";
  } else if (task_result.includes("POP2")) {
    document.getElementById('lipidSelect').value = "POP2";
  } else {
    var item = task_result[Math.floor(Math.random() * task_result.length)]
    document.getElementById('lipidSelect').value = item

  }

  radii_select_list = []
  radii_list = []
  float_string = "";
  for (i = 0; i < radii.length; i++) {
      if (radii[i] == "," || radii[i] == "]" || radii[i] == " ") {
          radii_list.push(float_string)
          radii_select_list.push([new String(float_string), new String (float_string)])
          float_string = "";
      } else {
          if (radii[i] == "[") {
              continue
          }
          float_string = float_string + radii[i]
      }
  }


  var radiiButton = createSelect(
    radii_select_list, {
    id: 'radiiSelect',
    onchange: function (e) {
      state = document.getElementById("button_heatmap").state;
      label_state = document.getElementById("label_button").state;

      if (state) {

        radius = document.getElementById("radiiSelect").value;
        lipid = document.getElementById("lipidSelect").value;
        param = document.getElementById("paramSelect").value;

        bfactor_to_load = radius + '_' + lipid + '_' + param

        if (bfactors.hasOwnProperty(bfactor_to_load)) {
          reprlist = stage.compList[0].reprList
          for (let i = 0; i < reprlist.length; i++) {
            const e = reprlist[i];
            if (e.name == "surface") {

              surface.setParameters({
                colorScheme: "white"
              })

              e.parent.structure.atomStore.bfactor = bfactors[bfactor_to_load]
              surface.setParameters({
                colorScheme: "bfactor"
              })

            }
          }

        } else {

          fetch('/media/user-data/' + username + '/' + task_id + '/' + 'data.json')
            .then((response) => {
              return response.json();
            })
            .then((actual_JSON) => {
              reprlist = stage.compList[0].reprList
              for (let i = 0; i < reprlist.length; i++) {
                const e = reprlist[i];
                if (e.name == "surface") {

                  surface.setParameters({
                    colorScheme: "white"
                  })

                  e.parent.structure.atomStore.bfactor = actual_JSON[bfactor_to_load]
                  surface.setParameters({
                    colorScheme: "bfactor"
                  })

                }
              }
            });
          }

        if (label_state) {
          labels.toggleVisibility();
          set_label_state(label_state);
          document.getElementById("label_text").hidden = true;
          document.getElementById("label_slider").hidden = true;

        }

      }

    }
  })
  addElement(radiiButton)

  var paramButton = createSelect([
    ["NUMBER", "NUMBER"],
    ["DURATION", "DURATION"]
  ], {
    id: 'paramSelect',
    onchange: function (e) {
      state = document.getElementById("button_heatmap").state;
      label_state = document.getElementById("label_button").state;

      if (state) {

        radius = document.getElementById("radiiSelect").value;
        lipid = document.getElementById("lipidSelect").value;
        param = document.getElementById("paramSelect").value;

        bfactor_to_load = radius + '_' + lipid + '_' + param
        if (bfactors.hasOwnProperty(bfactor_to_load)) {
          reprlist = stage.compList[0].reprList
          for (let i = 0; i < reprlist.length; i++) {
            const e = reprlist[i];
            if (e.name == "surface") {

              surface.setParameters({
                colorScheme: "white"
              })

              e.parent.structure.atomStore.bfactor = bfactors[bfactor_to_load]
              surface.setParameters({
                colorScheme: "bfactor"
              })

            }
          }

        } else {

          fetch('/media/user-data/' + username + '/' + task_id + '/' + 'data.json')
            .then((response) => {
              return response.json();
            })
            .then((actual_JSON) => {
              reprlist = stage.compList[0].reprList
              for (let i = 0; i < reprlist.length; i++) {
                const e = reprlist[i];
                if (e.name == "surface") {

                  surface.setParameters({
                    colorScheme: "white"
                  })

                  e.parent.structure.atomStore.bfactor = actual_JSON[bfactor_to_load]
                  surface.setParameters({
                    colorScheme: "bfactor"
                  })

                }
              }
            });
          }

        if (label_state) {
          labels.toggleVisibility();
          set_label_state(label_state);
          document.getElementById("label_text").hidden = true;
          document.getElementById("label_slider").hidden = true;

        }

      }
    }
  })
  addElement(paramButton)

  addElement(createElement("span", {
    id: 'radii_text',
    innerText: "Radius:"
  }))

  addElement(createElement("span", {
    id: 'param_text',
    innerText: "Metric:"
  }))

  var loadDXButton = createElement("input", {
    id: "button_loaddx",
    type: "button",
    value: "Load Density",
    onclick: function (e) {

      // get the current state of the button
      state = document.getElementById("button_loaddx").state;
      var vheight = stage.viewer.height;
      var vwidth = stage.viewer.width;
      console.log(vheight, vwidth)

      if (state) {
        compList = stage.compList
        for (let i = 0; i < compList.length; i++) {
          const e = compList[i];
          if (e.type == "volume") {
            stage.removeComponent(e)
          }
        }
        stage.viewer.height = vheight;
        stage.viewer.width = vwidth;
        console.log(vheight, vwidth)
        // update button states
        document.getElementById('surface_type').hidden = true;
        document.getElementById("button_loaddx").state = false;
        document.getElementById("button_loaddx").value = "Load Density";
        document.getElementById("toggle_density").hidden = true;
        document.getElementById("toggle_slice").hidden = true;
        document.getElementById('slice_text').hidden = true;
        document.getElementById('slice_slider').hidden = true;
        document.getElementById('slice_direction').hidden = true;
        document.getElementById('density_warning').hidden = false;

        isolevelCHOLText.innerText = ""

      } else {
        // load density
        var lipid = document.getElementById('lipidSelect').value;
        cp_index = get_array_index(lipid);
        Pace.restart()
        loadCHOL("/media/user-data/" + username + "/" + task_id + "/" + task_id + "_" + lipid + "_final.dx", color_palette[cp_index]);

        // update button state
        document.getElementById('surface_type').hidden = false;
        document.getElementById("button_loaddx").state = true;
        document.getElementById("button_loaddx").value = "Remove Density";
        document.getElementById("toggle_density").hidden = false;
        document.getElementById("toggle_slice").hidden = false;
        document.getElementById('slice_text').hidden = false;
        document.getElementById('slice_slider').hidden = false;
        document.getElementById('slice_direction').hidden = false;
        document.getElementById('density_warning').hidden = true;

      }
    }
  })
  addElement(loadDXButton)
  // initialize button state as false (no density file is loaded by default)
  document.getElementById("button_loaddx").state = false;

  // addElement(createElement("span", {
  //   id: 'density_warning',
  //   innerText: "Warning: file size ~15MB"
  // }))

  addElement(createElement("span", {
    id: 'density_warning',
    innerText: "Density viewing options:"
  }))

  var heatmapButton = createElement("input", {
    id: "button_heatmap",
    type: "button",
    value: "Show Contacts",
    onclick: function (e) {

      state = document.getElementById("button_heatmap").state;

      if (state) {

        reprlist = stage.compList[0].reprList
        for (let i = 0; i < reprlist.length; i++) {
          const e = reprlist[i];
          if (e.name == "surface") {

            e.parent.structure.atomStore.bfactor = 0
            surface.setParameters({
              colorScheme: "white"
            })
          }
        };
        document.getElementById("button_heatmap").value = "Show Contacts"
        document.getElementById("button_heatmap").state = false;

      } else {

        radius = document.getElementById("radiiSelect").value;
        lipid = document.getElementById("lipidSelect").value;
        param = document.getElementById("paramSelect").value;

        bfactor_to_load = radius + '_' + lipid + '_' + param

        if (bfactors.hasOwnProperty(bfactor_to_load)) {
          reprlist = stage.compList[0].reprList
          for (let i = 0; i < reprlist.length; i++) {
            const e = reprlist[i];
            if (e.name == "surface") {

              surface.setParameters({
                colorScheme: "white"
              })

              e.parent.structure.atomStore.bfactor = bfactors[bfactor_to_load]
              surface.setParameters({
                colorScheme: "bfactor"
              })

            }
          }

        } else {

          fetch('/media/user-data/' + username + '/' + task_id + '/' + 'data.json')
            .then((response) => {
              return response.json();
            })
            .then((actual_JSON) => {
              reprlist = stage.compList[0].reprList
              for (let i = 0; i < reprlist.length; i++) {
                const e = reprlist[i];
                if (e.name == "surface") {

                  surface.setParameters({
                    colorScheme: "white"
                  })

                  e.parent.structure.atomStore.bfactor = actual_JSON[bfactor_to_load]
                  surface.setParameters({
                    colorScheme: "bfactor"
                  })

                }
              }
            });
        };
        document.getElementById("button_heatmap").value = "Hide Contacts"
        document.getElementById("button_heatmap").state = true;

      }
    }
  })
  addElement(heatmapButton)
  document.getElementById("button_heatmap").state = false;

  addElement(createElement("span", {
    id: 'heatmap_text',
    innerText: "Heatmaps:"
  }))

  // A few surface representations for the density maps.
  var surfaceSelect = createSelect([
    ["smooth", "smooth"],
    ["wireframe", "wireframe"],
    ["contour", "contour"],
    ["flat", "flat"]
  ], {
    id: 'surface_type',
    onchange: function (e) {
      var v = e.target.value
      var p
      if (v === "contour") {
        p = {
          contour: true,
          flatShaded: false,
          opacity: 1,
          metalness: 0,
          wireframe: false
        }
      } else if (v === "wireframe") {
        p = {
          contour: false,
          flatShaded: false,
          opacity: 1,
          metalness: 0,
          wireframe: true
        }
      } else if (v === "smooth") {
        p = {
          contour: false,
          flatShaded: false,
          opacity: 0.7,
          metalness: 0,
          wireframe: false
        }
      } else if (v === "flat") {
        p = {
          contour: false,
          flatShaded: true,
          opacity: 0.7,
          metalness: 0.2,
          wireframe: false
        }
      }
      stage.getRepresentationsByName("surface").list[1].setParameters(p)
    }
  })
  addElement(surfaceSelect)
  document.getElementById('surface_type').hidden = true;

  // Button to select the direction of the slice representation.
  var sliceDirection = createSelect([
    ["x", "x"],
    ["y", "y"],
    ["z", "z"]
  ], {
    id: 'slice_direction',
    onchange: function (e) {
      var v = e.target.value
      var p
      if (v === "x") {
        p = {
          dimension: "x",
        }
      } else if (v === "y") {
        p = {
          dimension: "y"
        }
      } else if (v === "z") {
        p = {
          dimension: "z"
        }
      }
      stage.getRepresentationsByName("slice").setParameters(p)
    }
  })
  addElement(sliceDirection)
  document.getElementById('slice_direction').hidden = true;

  // Button to toggle the visibility of the cholesterol density.
  var toggleDXButton = createElement("input", {
    id: "toggle_density",
    type: "button",
    value: "Toggle Density",
    onclick: function (e) {
      surfCHOL.toggleVisibility()
    }
  })
  addElement(toggleDXButton)
  document.getElementById("toggle_density").hidden = true;

  // Button to toggle the visibility of the cholesterol slice representation.
  var toggleSliceButton = createElement("input", {
    id: "toggle_slice",
    type: "button",
    value: "Toggle Slice",
    onclick: function (e) {
      sliceReprCHOL.toggleVisibility()
    }
  })
  addElement(toggleSliceButton)
  document.getElementById("toggle_slice").hidden = true;


  function set_label_state(label_state) {
    if (label_state) {
      document.getElementById("label_button").value = "Show Labels";
      document.getElementById("label_button").state = false;
    } else {
      document.getElementById("label_button").value = "Hide Labels";
      document.getElementById("label_button").state = true;
    }
  }

  // Button to toggle the visibility of the label representaion.
  var toggleLabelButton = createElement("input", {
    id: "label_button",
    type: "button",
    value: "Show Labels",
    onclick: function (e) {

      heatmap_state = document.getElementById("button_heatmap").state;
      label_state = document.getElementById("label_button").state;

      var slider2 = document.getElementById("slider2")

      if (heatmap_state) {

        var bf = Array.from(labels.parent.structure.atomStore.bfactor);
        var bfMax = Math.max.apply(null, bf);
        labels.setParameters({
          radiusType: "bfactor",
          radiusScale: getBfMax(bfMax)
        })
        labels.toggleVisibility();
        set_label_state(label_state);

        document.getElementById("label_text").hidden = false;
        document.getElementById("label_slider").hidden = false;

        slider2.max = bfMax + 0.1;

      } else {
        labels.setParameters({
          radiusType: "",
          radiusScale: 5
        })
        labels.toggleVisibility();
        set_label_state(label_state);

        document.getElementById("label_text").hidden = true;
        document.getElementById("label_slider").hidden = true;
      }
    }
  })
  addElement(toggleLabelButton)
  document.getElementById("label_button").state = false;

  addElement(createElement("span", {
    id: 'label_header',
    innerText: "Labeling options:"
  }))

  // Slider button to controll the position of the slice representation.
  addElement(createElement("span", {
    id: 'slice_text',
    innerText: "Slice control: "
  }))
  var slicePosition = createElement("input", {
    id: "slice_slider",
    type: "range",
    min: 1,
    max: 100,
    step: 0.1,
    oninput: function (e) {
      stage.getRepresentationsByName("slice").setParameters({
        position: parseInt(e.target.value)
      })
    }
  })
  addElement(slicePosition)

  document.getElementById('slice_text').hidden = true;
  document.getElementById('slice_slider').hidden = true;

  // Slider button to controll the cutoff of the label representation.
  addElement(createElement("span", {
    id: 'label_text',
    innerText: "Label cutoff:"
  }))
  var lMax = 60.0
  var labelPosition = createElement("input", {
    id: "label_slider",
    type: "range",
    value: 10,
    min: 0,
    max: parseFloat(lMax),
    step: 0.1,
    oninput: function (e) {
      var labelUpdate = stage.getRepresentationsByName("label");
      labelUpdate = labelUpdate['list'][0]

      stage.getRepresentationsByName("label").setParameters({
        showL: showLabel(labelUpdate, e.target.value)
      })
    }
  })
  addElement(labelPosition)
  document.getElementById("label_text").hidden = true;
  document.getElementById("label_slider").hidden = true;

  // Button to take a screenshot.
  var screenshotButton = createElement("input", {
    id: "button5",
    type: "button",
    value: "Screenshot ",
    onclick: function () {
      stage.makeImage({
        factor: 1,
        antialias: false,
        trim: false,
        transparent: false
      }).then(function (blob) {
        NGL.download(blob, "screenshot.png")
      })
    }
  })
  addElement(screenshotButton)

  // Text to indicate the cholesterol isolevel density.
  var isolevelCHOLText = createElement(
    "div", {
      id: 'lipid_isolevel'
    }
  )
  addElement(isolevelCHOLText)

  // Add the text "GPCR structure:" to the screen. That's it.
  var gpcrStructureText = createElement("div", {
    innerText: "",
    id: 'gpcr_struc_text'
  })
  addElement(gpcrStructureText)

  // Text position for the name of each GPCR. The names are defined
  // when the structure is loaded.
  var gpcrNameText = createElement("div", {
    innerText: "",
    id: 'gpcr_text'
  })
  addElement(gpcrNameText)

  addElement(createElement("div", {
    id: 'lipid_text',
    innerText: "Showing lipid: "
  }))

  // Add the ctrl+scroll mouse behaviour to controll the density isolevels.
  stage.mouseControls.add("scroll-shift", function () {
    if (surfCHOL) {
      var levelCHOL = surfCHOL.getParameters().isolevel.toFixed(2)
      isolevelCHOLText.innerText = "Lipid level: " + levelCHOL + "\u03C3"
    }
  })

  function get_array_index(i_n) {
    for (i = 0; i < task_result.length; i++) {
      if (task_result[i] == i_n) {
        return i
      }
    }
  }

  // Density coloring.
  if (task_result.length <= 11) {
    var color_palette = palette('cb-Spectral', task_result.length)
  } else {
    var color_palette = palette('cb-Spectral', 11)
    var it = 0
    while (color_palette.length < task_result.length) {
      color_palette.push(color_palette[it]);
      it++;
    }
  }

  var bfactors = {}
  prot_loaded = false;

  function loadGPCR(id) {

    stage.setParameters({
      quality: "auto"
    })

    if (prot_loaded == false) {
      fetch('/media/user-data/' + username + '/' + task_id + '/' + 'data.json')
        .then((response) => {
          return response.json();
        })
        .then((json_file) => {
          for (let [key, value] of Object.entries(json_file)) {
            bfactors[key] = value
          }
        });

      function numb() {
        loadStructure("/media/user-data/" + username + "/" + task_id + "/" + prot_name + "_BB.pdb");
      };

      function call_numb() {
        return Promise.all([numb()])
      }
      call_numb()
        .then(function (t) {
          prot_loaded = true;
        });
    } else {
      compList = stage.compList
      for (let i = 0; i < compList.length; i++) {
        const e = compList[i];
        if (e.type == "volume") {
          stage.removeComponent(e)
        }
      }
      surface.setParameters({
        colorScheme: "white"
      })

      document.getElementById('surface_type').hidden = true;
      document.getElementById("button_loaddx").state = false;
      document.getElementById("button_loaddx").value = "Load Density";
      document.getElementById("toggle_density").hidden = true;
      document.getElementById("toggle_slice").hidden = true;
      document.getElementById('slice_text').hidden = true;
      document.getElementById('slice_slider').hidden = true;
      document.getElementById('slice_direction').hidden = true;
      document.getElementById('density_warning').hidden = false;

      isolevelCHOLText.innerText = ""

      document.getElementById("button_heatmap").state = false;
      document.getElementById("button_heatmap").value = "Show Contacts"
      document.getElementById("button_loaddx").state = false;
      document.getElementById("button_loaddx").value = "Load Density";
    }
  }

  // The default GPCR to load.
  //NOTE: select the first lipid
  loadGPCR(task_result[0]);

});
