use rodio::{Decoder, OutputStream, Sink};
use std::io::Cursor;
use tokio::net::TcpListener;
use tokio::io::AsyncReadExt;
use std::sync::Arc;

#[tokio::main]
async fn main() {
    println!("Iniciando Abril Rust Exo-skeleton...");

    // Inicializar el sistema de audio
    let (_stream, stream_handle) = OutputStream::try_default().expect("No se encontró dispositivo de audio");
    let sink = Sink::try_new(&stream_handle).expect("Error creando el Sink de audio");
    
    // Lo guardamos en un Arc para compartirlo
    let sink = Arc::new(sink);

    println!("Audio listo. Escuchando peticiones WAV en 127.0.0.1:9001...");
    let listener = TcpListener::bind("127.0.0.1:9001").await.unwrap();

    loop {
        match listener.accept().await {
            Ok((mut socket, _)) => {
                let sink = Arc::clone(&sink);
                
                tokio::spawn(async move {
                    let mut buf = Vec::new();
                    // Leer todo hasta que Python cierre la conexión
                    if let Ok(_) = socket.read_to_end(&mut buf).await {
                        if buf.is_empty() { return; }
                        
                        println!("Recibidos {} bytes de audio. Reproduciendo...", buf.len());
                        
                        // Intentar decodificar como WAV
                        let cursor = Cursor::new(buf);
                        match Decoder::new(cursor) {
                            Ok(source) => {
                                sink.append(source);
                            }
                            Err(e) => {
                                println!("Error decodificando audio: {:?}", e);
                            }
                        }
                    }
                });
            }
            Err(e) => println!("Error aceptando conexión: {:?}", e),
        }
    }
}
