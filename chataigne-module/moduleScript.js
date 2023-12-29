
function init() {
}

function cmdImport(title, file) {
  // load the metadata file as JSON
  var metadata = util.readFile(file, true);
  var folders = file.split("/");
  folders.splice(folders.length-1);
  folders = folders.join("/") + "/";

  // create the sequence and add the mp3 audio clip
  var seq = root.sequences.addItem();
  seq.totalTime.set(metadata.audioLength + 0.01);
  seq.setName(title);
  var audio = seq.layers.addItem("Audio");
  audio.setName(metadata.voiceName);
  var clip = audio.clips.addItem("AudioClip");
  clip.filePath.set(metadata.mp3File);

  // now add the automation layer and import the phonemes
  var mappingContainer = seq.layers.addItem("Mapping");
  mappingContainer.setName("Jaw Movements");
  // add the smoothing filter
  var smoothingFilter = mappingContainer.mapping.filters.addItem("Smooth");
  
  // add the default OSC output
  var output = mappingContainer.mapping.outputs.addItem();
  var cmd = output.setCommand("OSC", "", "Custom Message");
  cmd.address.set("/skeleton/jaw");
  cmd.arguments.addItem("Float");

  var automation = mappingContainer.automation;

  // a map of viseme name to 0 - 1 values, can be editedby tweaking the optons in chataigne
  // TODO: i think we can do this when the parameter changes so we dont have to do it every time
  var visemeList = local.parameters.visemeLevels.getTarget().getAllOptions();
  var visemeMap = {};
  if (visemeList) {
    for (i = 0 ; i < visemeList.length ; i++) {
      visemeMap[visemeList[i].key] = visemeList[i].value;
    }
  } else {
    visemeMap = {
      'e': 0.2,
      'k': 0.2,
      'a': 0.8,
      'p': 0,
      't': 0.3,
      'f': 0.1,
      'T': 0.3,
      's': 0.2,
      '@': 0.7,
      'E': 0.6,
      'S': 0.3,
      'u': 0.25,
      'O': 0.25,
    };
  }
  
  var data = metadata.results;
  for (i = 0 ; i < data.length ; i++) {
    var parts = data[i];
    if (!parts[0]) {
      continue ;
    }
    var value = visemeMap[parts[1]];
    if (!value) {
      value = 0;
    }
    automation.addKey(parts[0], value);
    automation.getKeyAtPosition(i).easingType.set("Hold");
  }
  // add a 0 at the end of the audio clip
  automation.addKey(metadata.audioLength, 0);
  automation.getKeyAtPosition(i+1).easingType.set("Hold");
}

function dataEvent(data, requestURL) {
  script.log("data event captured");
  script.log(data.mp3File);
  var baseDir = "./" + data.outputName;
  //var mp3FileName = baseDir + "/audio.mp3";
  var metadataFileName = baseDir + "/metadata.json";
  //data.mp3File = mp3FileName;
  
  script.log("creating base directory: " + baseDir);
  util.createDirectory(baseDir);

  //script.log("writing MP3 data to " + mp3FileName);
  //util.writeFile(mp3FileName, util.fromBase64(data.audio), true);

  script.log("writing metatadata to " + metadataFileName);
  util.writeFile(metadataFileName, JSON.stringify(data), true);

  // now invoke the viseme-generator import script
  cmdImport(data.outputName, metadataFileName);
}


function cmdGenerate(name, voiceName, emitRatio, text) {
  var params = {};
  params.dataType = "json";
  params.arguments = [
    "voiceName", voiceName,
    "text", text,
    "name", name,
  ];
  local.sendPOST("/generate", params);
}

function moduleParameterChanged(param) {
}

function moduleValueChanged(value) {
}
