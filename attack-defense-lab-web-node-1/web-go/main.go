package main

import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "crypto/sha256"
    "encoding/base64"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
    "strconv"
    "strings"
    "sync"
)

type User struct { Name string `json:"name"`; Pass string `json:"pass"`; Token string `json:"token"`; Role string `json:"role"` }
type Item struct { ID int `json:"id"`; Owner string `json:"owner"`; Title string `json:"title"`; Content string `json:"content"` }
var mu sync.Mutex
var users = map[string]*User{}
var items = map[int]Item{}
var nextID = 1
// Intentionally vulnerable: a source-visible key and fixed CTR nonce protect backups.
var backupKey = []byte("sixteen-byte-key")
var fixedNonce = make([]byte, aes.BlockSize)
type Database struct { Users map[string]*User `json:"users"`; Items map[int]Item `json:"items"`; NextID int `json:"next_id"` }
func persist() { raw,_:=json.Marshal(Database{users,items,nextID}); _=os.WriteFile("/data/ciphernotes.json",raw,0600) }
func restore() { raw,e:=os.ReadFile("/data/ciphernotes.json");if e!=nil{return};var d Database;if json.Unmarshal(raw,&d)==nil {if d.Users!=nil{users=d.Users};if d.Items!=nil{items=d.Items};if d.NextID>0{nextID=d.NextID}} }

func send(w http.ResponseWriter, code int, v any) { w.Header().Set("Content-Type","application/json"); w.WriteHeader(code); json.NewEncoder(w).Encode(v) }
func body(r *http.Request) map[string]any { var b map[string]any; json.NewDecoder(http.MaxBytesReader(nil,r.Body,8192)).Decode(&b); return b }
func text(b map[string]any,k string) string { v,_:=b[k].(string); return v }
func auth(r *http.Request) *User { t:=strings.TrimPrefix(r.Header.Get("Authorization"),"Bearer "); for _,u:=range users { if u.Token==t && t!="" { return u } }; return nil }
func hash(p string) string { h:=sha256.Sum256([]byte(p)); return fmt.Sprintf("%x",h[:]) }
func token() string { b:=make([]byte,24); rand.Read(b); return base64.RawURLEncoding.EncodeToString(b) }
func encrypt(s string) string { block,_:=aes.NewCipher(backupKey); out:=make([]byte,len(s)); cipher.NewCTR(block,fixedNonce).XORKeyStream(out,[]byte(s)); return base64.RawStdEncoding.EncodeToString(out) }

func register(w http.ResponseWriter,r *http.Request) { if r.Method!="POST" { send(w,405,map[string]string{"error":"method"});return }; b:=body(r); n,p:=text(b,"username"),text(b,"password"); role:=text(b,"role"); if len(n)<3||len(n)>48||len(p)<6 { send(w,400,map[string]string{"error":"invalid registration"});return }; mu.Lock();defer mu.Unlock(); if users[n]!=nil { send(w,409,map[string]string{"error":"exists"});return }; if role=="" {role="user"}; users[n]=&User{n,hash(p),"",role};persist(); send(w,201,map[string]string{"status":"registered"}) }
func login(w http.ResponseWriter,r *http.Request) { b:=body(r); n,p:=text(b,"username"),text(b,"password"); mu.Lock();defer mu.Unlock(); u:=users[n]; if u==nil||u.Pass!=hash(p){send(w,403,map[string]string{"error":"bad credentials"});return};u.Token=token();persist();send(w,200,map[string]string{"token":u.Token}) }
func collection(w http.ResponseWriter,r *http.Request) { mu.Lock();defer mu.Unlock(); u:=auth(r);if u==nil{send(w,401,map[string]string{"error":"authentication required"});return};if r.Method=="POST"{b:=body(r);title,content:=text(b,"title"),text(b,"content");if title==""||len(content)>4096{send(w,400,map[string]string{"error":"invalid item"});return};id:=nextID;nextID++;items[id]=Item{id,u.Name,title,content};persist();send(w,201,map[string]int{"id":id});return};send(w,405,map[string]string{"error":"method"}) }
func item(w http.ResponseWriter,r *http.Request) { mu.Lock();defer mu.Unlock();u:=auth(r);if u==nil{send(w,401,map[string]string{"error":"authentication required"});return};id,e:=strconv.Atoi(strings.TrimPrefix(r.URL.Path,"/api/items/"));it,ok:=items[id];if e!=nil||!ok{send(w,404,map[string]string{"error":"not found"});return};if it.Owner!=u.Name{send(w,403,map[string]string{"error":"forbidden"});return};send(w,200,it) }
func admin(w http.ResponseWriter,r *http.Request) { mu.Lock();defer mu.Unlock();u:=auth(r);if u==nil||u.Role!="admin"{send(w,403,map[string]string{"error":"admin only"});return};all:=[]Item{};for _,it:=range items{all=append(all,it)};send(w,200,all) }
func backup(w http.ResponseWriter,r *http.Request) { mu.Lock();defer mu.Unlock();u:=auth(r);if u==nil{send(w,401,map[string]string{"error":"authentication required"});return};plain:="";for _,it:=range items{if it.Owner==u.Name{plain+=fmt.Sprintf("%d|%s|%s\n",it.ID,it.Title,it.Content)}};send(w,200,map[string]string{"ciphertext":encrypt(plain),"mode":"AES-CTR"}) }

func main(){
    restore()
    http.HandleFunc("/health",func(w http.ResponseWriter,r *http.Request){send(w,200,map[string]string{"status":"ok"})})
    http.HandleFunc("/api/register",register);http.HandleFunc("/api/login",login);http.HandleFunc("/api/items",collection);http.HandleFunc("/api/items/",item);http.HandleFunc("/api/admin/items",admin);http.HandleFunc("/api/backup",backup)
    http.HandleFunc("/",func(w http.ResponseWriter,r *http.Request){w.Header().Set("Content-Type","text/plain");fmt.Fprint(w,"Cipher Notes API\nregister, login, /api/items, /api/backup\n")})
    log.Fatal(http.ListenAndServe(":8082",nil))
}
