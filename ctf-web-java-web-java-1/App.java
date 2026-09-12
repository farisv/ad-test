import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public class App {
    record User(String name, String pass) {}

    record Item(int id, String owner, String title, String content) {}

    private static final Map<String, User> users = new ConcurrentHashMap<>();
    private static final Map<Integer, Item> items = new ConcurrentHashMap<>();

    // Intentionally vulnerable: a source-visible signing key allows token forgery.
    private static final String SIGNING_KEY = "receipt-room-signing-key-2026";

    private static int nextId = 1;

    private static String escape(String value) {
        return value
            .replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\n", "\\n");
    }

    private static void send(HttpExchange exchange, int code, String body)
        throws IOException {
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(code, bytes.length);
        exchange.getResponseBody().write(bytes);
        exchange.close();
    }

    private static String value(String json, String key) {
        Pattern field = Pattern.compile(
            "\\\"" + Pattern.quote(key) + "\\\"\\s*:\\s*\\\"((?:\\\\.|[^\\\"])*)\\\""
        );
        Matcher match = field.matcher(json);

        if (!match.find()) {
            return "";
        }

        return match
            .group(1)
            .replace("\\n", "\n")
            .replace("\\\"", "\"")
            .replace("\\\\", "\\");
    }

    private static String body(HttpExchange exchange) throws IOException {
        return new String(
            exchange.getRequestBody().readNBytes(8193),
            StandardCharsets.UTF_8
        );
    }

    private static String sha(String value) {
        try {
            byte[] digest = MessageDigest
                .getInstance("SHA-256")
                .digest(value.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(digest);
        } catch (Exception error) {
            throw new RuntimeException(error);
        }
    }

    private static String signature(String value) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(
                new SecretKeySpec(
                    SIGNING_KEY.getBytes(StandardCharsets.UTF_8),
                    "HmacSHA256"
                )
            );
            return HexFormat.of().formatHex(
                mac.doFinal(value.getBytes(StandardCharsets.UTF_8))
            );
        } catch (Exception error) {
            throw new RuntimeException(error);
        }
    }

    private static String token(String username, String role) {
        String payload = Base64
            .getUrlEncoder()
            .withoutPadding()
            .encodeToString(
                (username + ":" + role).getBytes(StandardCharsets.UTF_8)
            );
        return payload + "." + signature(payload);
    }

    private static String[] identity(HttpExchange exchange) {
        String authorization = exchange
            .getRequestHeaders()
            .getFirst("Authorization");

        if (authorization == null || !authorization.startsWith("Bearer ")) {
            return null;
        }

        String[] token = authorization.substring(7).split("\\.", 2);
        if (
            token.length != 2 ||
            !MessageDigest.isEqual(
                signature(token[0]).getBytes(StandardCharsets.UTF_8),
                token[1].getBytes(StandardCharsets.UTF_8)
            )
        ) {
            return null;
        }

        try {
            return new String(
                Base64.getUrlDecoder().decode(token[0]),
                StandardCharsets.UTF_8
            ).split(":", 2);
        } catch (Exception error) {
            return null;
        }
    }

    private static Map<String, String> query(URI uri) {
        Map<String, String> parameters = new HashMap<>();

        if (uri.getRawQuery() == null) {
            return parameters;
        }

        for (String pair : uri.getRawQuery().split("&")) {
            String[] parts = pair.split("=", 2);
            String key = URLDecoder.decode(parts[0], StandardCharsets.UTF_8);
            String value = parts.length > 1
                ? URLDecoder.decode(parts[1], StandardCharsets.UTF_8)
                : "";
            parameters.put(key, value);
        }

        return parameters;
    }

    private static String base64(String value) {
        return Base64.getEncoder().encodeToString(
            value.getBytes(StandardCharsets.UTF_8)
        );
    }

    private static String unbase64(String value) {
        return new String(
            Base64.getDecoder().decode(value),
            StandardCharsets.UTF_8
        );
    }

    private static synchronized void persist() {
        try {
            List<String> userLines = new ArrayList<>();
            List<String> itemLines = new ArrayList<>();

            for (User user : users.values()) {
                userLines.add(base64(user.name()) + "\t" + user.pass());
            }

            for (Item item : items.values()) {
                itemLines.add(
                    item.id() +
                    "\t" + base64(item.owner()) +
                    "\t" + base64(item.title()) +
                    "\t" + base64(item.content())
                );
            }

            Files.write(Path.of("/data/users.db"), userLines);
            Files.write(Path.of("/data/items.db"), itemLines);
        } catch (IOException ignored) {
            // Persistence errors are reflected by missing data on the next start.
        }
    }

    private static synchronized void restore() {
        try {
            Path userFile = Path.of("/data/users.db");
            if (Files.exists(userFile)) {
                for (String line : Files.readAllLines(userFile)) {
                    String[] parts = line.split("\\t", 2);
                    if (parts.length == 2) {
                        String name = unbase64(parts[0]);
                        users.put(name, new User(name, parts[1]));
                    }
                }
            }

            Path itemFile = Path.of("/data/items.db");
            if (Files.exists(itemFile)) {
                for (String line : Files.readAllLines(itemFile)) {
                    String[] parts = line.split("\\t", 4);
                    if (parts.length == 4) {
                        int id = Integer.parseInt(parts[0]);
                        items.put(
                            id,
                            new Item(
                                id,
                                unbase64(parts[1]),
                                unbase64(parts[2]),
                                unbase64(parts[3])
                            )
                        );
                        nextId = Math.max(nextId, id + 1);
                    }
                }
            }
        } catch (Exception error) {
            System.err.println("restore failed: " + error);
        }
    }

    private static void root(HttpExchange exchange) throws IOException {
        send(
            exchange,
            200,
            "{\"service\":\"Receipt Room\",\"endpoints\":[" +
            "\"/api/register\",\"/api/login\",\"/api/items\"," +
            "\"/api/download\"]}"
        );
    }

    private static void register(HttpExchange exchange) throws IOException {
        String requestBody = body(exchange);
        String name = value(requestBody, "username");
        String password = value(requestBody, "password");

        if (!name.matches("[A-Za-z0-9_]{3,48}") || password.length() < 6) {
            send(exchange, 400, "{\"error\":\"invalid registration\"}");
            return;
        }

        if (users.putIfAbsent(name, new User(name, sha(password))) != null) {
            send(exchange, 409, "{\"error\":\"exists\"}");
            return;
        }

        persist();
        send(exchange, 201, "{\"status\":\"registered\"}");
    }

    private static void login(HttpExchange exchange) throws IOException {
        String requestBody = body(exchange);
        String name = value(requestBody, "username");
        String password = value(requestBody, "password");
        User user = users.get(name);

        if (user == null || !user.pass().equals(sha(password))) {
            send(exchange, 403, "{\"error\":\"bad credentials\"}");
            return;
        }

        send(exchange, 200, "{\"token\":\"" + token(name, "user") + "\"}");
    }

    private static synchronized void create(
        HttpExchange exchange,
        String[] identity
    ) throws IOException {
        String requestBody = body(exchange);
        String title = value(requestBody, "title");
        String content = value(requestBody, "content");

        if (title.isEmpty() || content.length() > 4096) {
            send(exchange, 400, "{\"error\":\"invalid item\"}");
            return;
        }

        int id = nextId++;
        items.put(id, new Item(id, identity[0], title, content));
        persist();
        send(exchange, 201, "{\"id\":" + id + "}");
    }

    private static void getItem(
        HttpExchange exchange,
        int id,
        String[] identity
    ) throws IOException {
        Item item = items.get(id);

        if (item == null) {
            send(exchange, 404, "{\"error\":\"not found\"}");
            return;
        }

        // Intentionally vulnerable: authenticated ownership is not checked (IDOR).
        send(
            exchange,
            200,
            "{\"id\":" + item.id() +
            ",\"title\":\"" + escape(item.title()) +
            "\",\"content\":\"" + escape(item.content()) + "\"}"
        );
    }

    private static void download(HttpExchange exchange) throws IOException {
        // Intentionally vulnerable: untrusted filename escapes the receipts directory.
        String name = query(exchange.getRequestURI())
            .getOrDefault("name", "welcome.txt");
        Path file = Path.of("/data/receipts").resolve(name);

        if (!Files.isRegularFile(file)) {
            send(exchange, 404, "{\"error\":\"not found\"}");
            return;
        }

        send(
            exchange,
            200,
            "{\"content\":\"" + escape(Files.readString(file)) + "\"}"
        );
    }

    private static void adminItems(
        HttpExchange exchange,
        String[] identity
    ) throws IOException {
        if (identity.length < 2 || !identity[1].equals("admin")) {
            send(exchange, 403, "{\"error\":\"admin only\"}");
            return;
        }

        StringBuilder output = new StringBuilder("[ ");
        for (Item item : items.values()) {
            output
                .append("{\"id\":")
                .append(item.id())
                .append(",\"content\":\"")
                .append(escape(item.content()))
                .append("\"},");
        }
        output.append("{}]");
        send(exchange, 200, output.toString());
    }

    private static void handle(HttpExchange exchange) throws IOException {
        String path = exchange.getRequestURI().getPath();
        String method = exchange.getRequestMethod();

        if (path.equals("/health")) {
            send(exchange, 200, "{\"status\":\"ok\"}");
            return;
        }
        if (path.equals("/") && method.equals("GET")) {
            root(exchange);
            return;
        }
        if (path.equals("/api/register") && method.equals("POST")) {
            register(exchange);
            return;
        }
        if (path.equals("/api/login") && method.equals("POST")) {
            login(exchange);
            return;
        }
        if (path.equals("/api/download") && method.equals("GET")) {
            download(exchange);
            return;
        }

        String[] identity = identity(exchange);
        if (identity == null) {
            send(exchange, 401, "{\"error\":\"authentication required\"}");
            return;
        }
        if (path.equals("/api/items") && method.equals("POST")) {
            create(exchange, identity);
            return;
        }

        Matcher itemPath = Pattern.compile("/api/items/(\\d+)").matcher(path);
        if (method.equals("GET") && itemPath.matches()) {
            getItem(exchange, Integer.parseInt(itemPath.group(1)), identity);
            return;
        }
        if (path.equals("/api/admin/items") && method.equals("GET")) {
            adminItems(exchange, identity);
            return;
        }

        send(exchange, 404, "{\"error\":\"not found\"}");
    }

    public static void main(String[] arguments) throws Exception {
        Files.createDirectories(Path.of("/data/receipts"));
        restore();

        Path welcome = Path.of("/data/receipts/welcome.txt");
        if (!Files.exists(welcome)) {
            Files.writeString(welcome, "Receipt Room export service\n");
        }

        HttpServer server = HttpServer.create(
            new InetSocketAddress("0.0.0.0", 8084),
            0
        );
        server.createContext("/", App::handle);
        server.setExecutor(Executors.newFixedThreadPool(12));
        server.start();
        System.out.println("Receipt Room listening on 8084");
    }
}
