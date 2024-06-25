package com.corporate.riskmanagement.api;

import com.corporate.riskmanagement.services.AiService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@Slf4j
public class DocumentAPI {
    private final AiService aiService;

    String systemMessage = """
                "You are a financial analysis API specializing in statements.\n" +
                "Give precise answers to what you are asked from the information provided to you.\n" +
                "Only return a valid JSON response, without using phrases indicating an invalid response \n"+
                "Do not offer explanations or phrases and do not repeat yourself \n"
                "You need to determine the years for which the data has been presented and segregate the data according to the years.
                {information}
                
                Don't assume answers and do not answer more than required.Please provide only information that is present on the document in a valid JSON format""";

    @Autowired
    public DocumentAPI(AiService aiService) {
        this.aiService = aiService;
    }

    @PostMapping("/vectorestore/clear")
    public String clearVectorStore() throws IOException {
       return aiService.clearVectorStore();
    }

    @PostMapping("/rag/document/")
    public Object chatWithModelUsingVectorStore(@RequestParam MultipartFile file) throws IOException {
        return aiService.chatWithModelUsingVectorStore(file);
    }
}
