#ifndef CACTUS_WHISTLE_INTERFACE_H
#define CACTUS_WHISTLE_INTERFACE_H

#include <string>
#include <vector>

// Mock interface for Cactus Whistle speech recognition
class CactusWhistleInterface {
public:
    // Initialize the speech recognition engine
    bool initialize(const std::string& model_path = "");
    
    // Transcribe audio to text
    std::string transcribe(const std::vector<uint8_t>& audio_data);
    
    // Transcribe audio file
    std::string transcribe_file(const std::string& audio_file_path);
    
    // Get supported languages
    std::vector<std::string> get_supported_languages();
    
    // Set language for transcription
    bool set_language(const std::string& language);
    
    // Get model information
    std::string get_model_info();
    
    // Cleanup resources
    void cleanup();
};

// Mock function to demonstrate usage
void demo_cactus_whistle_usage();

#endif // CACTUS_WHISTLE_INTERFACE_H