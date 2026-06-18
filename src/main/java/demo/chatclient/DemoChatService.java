package demo.chatclient;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.stereotype.Service;

@Service
public class DemoChatService implements DemoChatClient {

    private final ChatClient chatClient;

    public DemoChatService(ChatClient.Builder chatClientBuilder) {
        this.chatClient = chatClientBuilder.build();
    }

    @SuppressWarnings("null")
    @Override
    public Answer askQuestion(Question question) {
        var response = chatClient.prompt()
            .user(question.question())
            .call()
            .content();
        return new Answer(response);
    }
}