import java.awt.*;
import java.net.URI;
import java.net.http.*;
import java.net.http.HttpRequest.BodyPublishers;
import java.net.http.HttpResponse.BodyHandlers;
import javax.swing.*;

public class JarvisClient {

    private static final String SERVER_URL = "http://127.0.0.1:8000/jarvis";

    public static void main(String[] args) {
        JFrame frame = new JFrame("Jarvis Client");
        frame.setSize(500, 600);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        JTextArea chatArea = new JTextArea();
        chatArea.setEditable(false);
        chatArea.setLineWrap(true);
        JScrollPane scroll = new JScrollPane(chatArea);
        frame.add(scroll, BorderLayout.CENTER);

        JTextField inputField = new JTextField();
        frame.add(inputField, BorderLayout.SOUTH);

        inputField.addActionListener(e -> {
            String text = inputField.getText().trim();
            if(!text.isEmpty()){
                chatArea.append("You: " + text + "\n");
                String reply = sendCommand(text);
                chatArea.append("Jarvis: " + reply + "\n");
                inputField.setText("");
            }
        });

        frame.setVisible(true);
    }

    public static String sendCommand(String text){
        try{
            HttpClient client = HttpClient.newHttpClient();
            String json = "{\"text\":\"" + text + "\"}";
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(SERVER_URL))
                .header("Content-Type", "application/json")
                .POST(BodyPublishers.ofString(json))
                .build();
            HttpResponse<String> response = client.send(request, BodyHandlers.ofString());
            // parse simple JSON manually
            String body = response.body();
            int idx = body.indexOf("reply\":\"");
            if(idx>=0){
                String temp = body.substring(idx+8);
                temp = temp.replaceAll("\"}","").replaceAll("\\\\n","\n");
                return temp;
            }
            return body;
        }catch(Exception e){
            e.printStackTrace();
            return "Error connecting to Jarvis brain.";
        }
    }
}