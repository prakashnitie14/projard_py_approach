package com.corporate.riskmanagement.aws;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.core.exception.SdkException;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.Channels;
import java.nio.channels.ReadableByteChannel;
import java.util.ArrayList;
import java.util.List;

@Service
@Slf4j
public class PersistenceService {
    private final S3Client s3Client;
    private final Region region;
    private final String RAW_DATA_BUCKET_NAME = "ard-input.txt";
    private String RAW_DATA_KEY = "src";

    public PersistenceService() {
        region = Region.CA_CENTRAL_1;
       s3Client = S3Client.builder()
                .region(region)
                .build();
    }

    public CompleteMultipartUploadResponse persistFile(MultipartFile file){
        try {
            ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(file.getBytes());
            RAW_DATA_KEY = file.getOriginalFilename();
           return multipartUploadWithS3Client(byteArrayInputStream);
        } catch (SdkException | IOException e) {
            log.error(e.getMessage());
        }
        return null;
    }

    public CompleteMultipartUploadResponse multipartUploadWithS3Client(ByteArrayInputStream inputStream) {
        // Initiate the multipart upload.
        CreateMultipartUploadResponse createMultipartUploadResponse = s3Client.createMultipartUpload(b -> b
                .bucket(RAW_DATA_BUCKET_NAME)
                .key(RAW_DATA_KEY));
        String uploadId = createMultipartUploadResponse.uploadId();

        // Upload the parts of the file.
        int partNumber = 1;
        List<CompletedPart> completedParts = new ArrayList<>();
        ByteBuffer bb = ByteBuffer.allocate(1024 * 1024 * 5); // 5 MB byte buffer

        try {
            long fileSize = inputStream.available();
            ReadableByteChannel readableByteChannel = Channels.newChannel(inputStream);
            int position = 0;
            while (position < fileSize) {
                int read =  readableByteChannel.read(bb);

                bb.flip(); // Swap position and limit before reading from the buffer.
                UploadPartRequest uploadPartRequest = UploadPartRequest.builder()
                        .bucket(RAW_DATA_BUCKET_NAME)
                        .key(RAW_DATA_KEY)
                        .uploadId(uploadId)
                        .partNumber(partNumber)
                        .build();

                UploadPartResponse partResponse = s3Client.uploadPart(
                        uploadPartRequest,
                        RequestBody.fromByteBuffer(bb));

                CompletedPart part = CompletedPart.builder()
                        .partNumber(partNumber)
                        .eTag(partResponse.eTag())
                        .build();
                completedParts.add(part);

                bb.clear();
                position += read;
                partNumber++;
            }
        } catch (IOException e) {
            log.error(e.getMessage());
        }

        // Complete the multipart upload.
       CompleteMultipartUploadResponse completeMultipartUploadResponse = s3Client.completeMultipartUpload(b -> b
                .bucket(RAW_DATA_BUCKET_NAME)
                .key(RAW_DATA_KEY)
                .uploadId(uploadId)
                .multipartUpload(CompletedMultipartUpload.builder().parts(completedParts).build()));
        return completeMultipartUploadResponse;
    }
}
