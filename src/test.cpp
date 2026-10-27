#include <iostream>
#include "cactus_whistle_interface.h"

int main() {
    std::cout << "=== Cactus Whistle Test ===" << std::endl;
    
    CactusWhistleInterface whisper;
    
    if (whisper.initialize()) {
        std::cout << "Engine initialized successfully!" << std::endl;
        std::cout << whisper.get_model_info() << std::endl;
        
        auto languages = whisper.get_supported_languages();
        std::cout << "Supported languages: ";
        for (const auto& lang : languages) {
            std::cout << lang << " ";
        }
        std::cout << std::endl;
        
        // Test transcription
        std::string result1 = whisper.transcribe_file("sample_audio.wav");
        std::cout << "File transcription result: " << result1 << std::endl;
        
        whisper.cleanup();
        std::cout << "Test completed successfully!" << std::endl;
    } else {
        std::cout << "Failed to initialize engine!" << std::endl;
        return 1;
    }
    
    return 0;
}