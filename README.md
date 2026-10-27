# AI Skeletons Speech Generation

This project implements speech generation capabilities for AI skeletons, with support for various speech recognition engines including a mock interface for Cactus Whistle.

## Features

- Mock interface for Cactus Whistle speech recognition
- Easy integration with existing projects
- Cross-platform compatibility
- Support for multiple languages

## Getting Started

### Prerequisites

- C++11 or later
- CMake 3.8 or later (for building)

### Building

```bash
mkdir build
cd build
cmake ..
make
```

### Usage

```cpp
#include "cactus_whistle_interface.h"

int main() {
    CactusWhistleInterface whisper;
    
    if (whisper.initialize()) {
        std::cout << whisper.get_model_info() << std::endl;
        
        // Transcribe audio file
        std::string result = whisper.transcribe_file("sample.wav");
        std::cout << "Transcription: " << result << std::endl;
        
        whisper.cleanup();
    }
    
    return 0;
}
```

## Cactus Whistle Integration

This mock interface provides a foundation for integrating with the real Cactus Whistle library. The actual implementation would:
- Load the .cact model files
- Interface with the C API functions (`needle_load`, `needle_transcribe`, `needle_embed`)
- Handle platform-specific deployments

## License

This project is licensed under the MIT License - see the LICENSE file for details.