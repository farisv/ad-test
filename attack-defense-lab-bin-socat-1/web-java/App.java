import com.sun.net.httpserver.*;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.regex.*;

public class App {
  record User(String name,String pass) {}
  record Item(int id,String owner,String title,String content) {}
  static final Map<String,User> users=new ConcurrentHashMap<>();
  static final Map<Integer,Item> items=new ConcurrentHashMap<>();
  // Intentionally vulnerable: a source-visible signing key allows token forgery.
  static final String SIGNING_KEY="receipt-room-signing-key-2026";
  static int nextId=1;
  static String esc(String s){return s.replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n");}
  static void send(HttpExchange x,int code,String body)throws IOException{x.getResponseHeaders().set("Content-Type","application/json");byte[]b=body.getBytes(StandardCharsets.UTF_8);x.sendResponseHeaders(code,b.length);x.getResponseBody().write(b);x.close();}
  static String val(String json,String key){Matcher m=Pattern.compile("\\\""+Pattern.quote(key)+"\\\"\\s*:\\s*\\\"((?:\\\\.|[^\\\"])*)\\\"").matcher(json);if(!m.find())return"";return m.group(1).replace("\\n","\n").replace("\\\"","\"").replace("\\\\","\\");}
  static String body(HttpExchange x)throws IOException{return new String(x.getRequestBody().readNBytes(8193),StandardCharsets.UTF_8);}
  static String sha(String s){try{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8)));}catch(Exception e){throw new RuntimeException(e);}}
  static String sig(String s){try{Mac m=Mac.getInstance("HmacSHA256");m.init(new SecretKeySpec(SIGNING_KEY.getBytes(StandardCharsets.UTF_8),"HmacSHA256"));return HexFormat.of().formatHex(m.doFinal(s.getBytes(StandardCharsets.UTF_8)));}catch(Exception e){throw new RuntimeException(e);}}
  static String token(String user,String role){String p=Base64.getUrlEncoder().withoutPadding().encodeToString((user+":"+role).getBytes(StandardCharsets.UTF_8));return p+"."+sig(p);}
  static String[] identity(HttpExchange x){String h=x.getRequestHeaders().getFirst("Authorization");if(h==null||!h.startsWith("Bearer "))return null;String[]t=h.substring(7).split("\\.",2);if(t.length!=2||!MessageDigest.isEqual(sig(t[0]).getBytes(),t[1].getBytes()))return null;try{return new String(Base64.getUrlDecoder().decode(t[0]),StandardCharsets.UTF_8).split(":",2);}catch(Exception e){return null;}}
  static Map<String,String> query(URI u){Map<String,String>q=new HashMap<>();if(u.getRawQuery()==null)return q;for(String p:u.getRawQuery().split("&")){String[]kv=p.split("=",2);q.put(URLDecoder.decode(kv[0],StandardCharsets.UTF_8),kv.length>1?URLDecoder.decode(kv[1],StandardCharsets.UTF_8):"");}return q;}
  static String b64(String s){return Base64.getEncoder().encodeToString(s.getBytes(StandardCharsets.UTF_8));}
  static String unb64(String s){return new String(Base64.getDecoder().decode(s),StandardCharsets.UTF_8);}
  static synchronized void persist() {try{List<String> ul=new ArrayList<>(),il=new ArrayList<>();for(User u:users.values())ul.add(b64(u.name())+"\t"+u.pass());for(Item i:items.values())il.add(i.id()+"\t"+b64(i.owner())+"\t"+b64(i.title())+"\t"+b64(i.content()));Files.write(Path.of("/data/users.db"),ul);Files.write(Path.of("/data/items.db"),il); }catch(IOException ignored){}}
  static synchronized void restore(){try{Path u=Path.of("/data/users.db");if(Files.exists(u))for(String line:Files.readAllLines(u)){String[]p=line.split("\\t",2);if(p.length==2){String n=unb64(p[0]);users.put(n,new User(n,p[1]));}}Path f=Path.of("/data/items.db");if(Files.exists(f))for(String line:Files.readAllLines(f)){String[]p=line.split("\\t",4);if(p.length==4){int id=Integer.parseInt(p[0]);items.put(id,new Item(id,unb64(p[1]),unb64(p[2]),unb64(p[3])));nextId=Math.max(nextId,id+1);}}}catch(Exception e){System.err.println("restore failed: "+e);}}
  static void root(HttpExchange x)throws IOException{send(x,200,"{\"service\":\"Receipt Room\",\"endpoints\":[\"/api/register\",\"/api/login\",\"/api/items\",\"/api/download\"]}");}
  static void register(HttpExchange x)throws IOException{String b=body(x),n=val(b,"username"),p=val(b,"password");if(!n.matches("[A-Za-z0-9_]{3,48}")||p.length()<6){send(x,400,"{\"error\":\"invalid registration\"}");return;}if(users.putIfAbsent(n,new User(n,sha(p)))!=null){send(x,409,"{\"error\":\"exists\"}");return;}persist();send(x,201,"{\"status\":\"registered\"}");}
  static void login(HttpExchange x)throws IOException{String b=body(x),n=val(b,"username"),p=val(b,"password");User u=users.get(n);if(u==null||!u.pass().equals(sha(p))){send(x,403,"{\"error\":\"bad credentials\"}");return;}send(x,200,"{\"token\":\""+token(n,"user")+"\"}");}
  static synchronized void create(HttpExchange x,String[]id)throws IOException{String b=body(x),t=val(b,"title"),c=val(b,"content");if(t.isEmpty()||c.length()>4096){send(x,400,"{\"error\":\"invalid item\"}");return;}int n=nextId++;items.put(n,new Item(n,id[0],t,c));persist();send(x,201,"{\"id\":"+n+"}");}
  static void getItem(HttpExchange x,int n,String[]id)throws IOException{Item i=items.get(n);if(i==null){send(x,404,"{\"error\":\"not found\"}");return;}// Intentionally vulnerable: authenticated ownership is not checked (IDOR).
    send(x,200,"{\"id\":"+i.id()+",\"title\":\""+esc(i.title())+"\",\"content\":\""+esc(i.content())+"\"}");}
  static void handle(HttpExchange x)throws IOException{String p=x.getRequestURI().getPath(),m=x.getRequestMethod();if(p.equals("/health")){send(x,200,"{\"status\":\"ok\"}");return;}if(p.equals("/")&&m.equals("GET")){root(x);return;}if(p.equals("/api/register")&&m.equals("POST")){register(x);return;}if(p.equals("/api/login")&&m.equals("POST")){login(x);return;}String[]id=identity(x);if(p.equals("/api/download")&&m.equals("GET")){// Intentionally vulnerable: untrusted filename escapes the receipts directory.
      Path f=Path.of("/data/receipts").resolve(query(x.getRequestURI()).getOrDefault("name","welcome.txt"));if(!Files.isRegularFile(f)){send(x,404,"{\"error\":\"not found\"}");return;}send(x,200,"{\"content\":\""+esc(Files.readString(f))+"\"}");return;}
    if(id==null){send(x,401,"{\"error\":\"authentication required\"}");return;}if(p.equals("/api/items")&&m.equals("POST")){create(x,id);return;}Matcher mm=Pattern.compile("/api/items/(\\d+)").matcher(p);if(m.equals("GET")&&mm.matches()){getItem(x,Integer.parseInt(mm.group(1)),id);return;}if(p.equals("/api/admin/items")&&m.equals("GET")){if(id.length<2||!id[1].equals("admin")){send(x,403,"{\"error\":\"admin only\"}");return;}StringBuilder out=new StringBuilder("[ ");for(Item i:items.values())out.append("{\"id\":").append(i.id()).append(",\"content\":\"").append(esc(i.content())).append("\"},");out.append("{}]");send(x,200,out.toString());return;}send(x,404,"{\"error\":\"not found\"}");}
  public static void main(String[]a)throws Exception{Files.createDirectories(Path.of("/data/receipts"));restore();Path w=Path.of("/data/receipts/welcome.txt");if(!Files.exists(w))Files.writeString(w,"Receipt Room export service\n");HttpServer s=HttpServer.create(new InetSocketAddress("0.0.0.0",8084),0);s.createContext("/",App::handle);s.setExecutor(Executors.newFixedThreadPool(12));s.start();System.out.println("Receipt Room listening on 8084");}
}
