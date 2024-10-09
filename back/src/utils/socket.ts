import { Socket, Server as SocketServer } from "socket.io";
import * as HTTP from "http";

export class SocketSingleton {

    private static instance: SocketSingleton = null;
    public io: SocketServer;
    public matrix_data: Number[][] = [[], [], [], [], [], []];
    public counter = 0;
    public selected_satellite: number = -1;

    public static getInstance(): SocketSingleton {
        if (!SocketSingleton.instance) {
            return null;
        }
        return SocketSingleton.instance;
    }

    public static createInstance(server: HTTP.Server) {
        if (!SocketSingleton.instance) {
            SocketSingleton.instance = new SocketSingleton(server);
        }
    }

    private constructor(server: HTTP.Server) {
        this.io = new SocketServer(server, {
            maxHttpBufferSize: 1e8,
            cors: {
                origin: "*",
                methods: ["GET", "POST"],
                credentials: true
            }
        });

        console.log("Socket server running on port 10001");

        this.io.on("connection", (socket: Socket) => {
            console.log("User connected");

            socket.on("join", (room: string) => {
                this.selected_satellite = parseInt(room);
                if (parseInt(room) != -1) {
                    console.log("Emitting big data");
                    let points_to_send = this.matrix_data[parseInt(room)].filter((value, index) => index % 48 == 0);
                    this.generateEvent("big_data", points_to_send);
                }
            });

            socket.on("satellite_data", async (data: any) => {
                console.log("Data received from satellite");

                for (let i = 0; i < data.length; i++) {
                    if (data[i].length > 0) {
                        this.matrix_data[i].push(...data[i]);
                    }
                }
                this.counter++;

                if (this.selected_satellite != -1) {
                    console.log("Emitting small data");
                    if (data[this.selected_satellite].length > 0) {
                        let points_to_send = data[this.selected_satellite].filter((value, index) => index % 48 == 0);
                        this.generateEvent("small_data", points_to_send);
                        console.log("Total data points for satellite " + this.selected_satellite + ": " + this.matrix_data[this.selected_satellite].length);
                    }
                }

                if (this.counter == 4) {
                    console.log("Prediccion");
                    this.counter = 0;

                    let analysis = true;
                    for (let i = 0; i < this.matrix_data.length; i++) {
                        if (this.matrix_data[i].length < 21000) {
                            console.log("Not enough data for analysis");
                            analysis = false;
                            break;
                        }
                    }
                    let matrix_data_filtered = null;

                    if (analysis) {
                        matrix_data_filtered = this.matrix_data.map(row => row.slice(-21000));

                        fetch("http://detector:10002/v1/api/detector/detect_seism", {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({matrices: matrix_data_filtered})
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Success:', data);
                        })
                        .catch((error) => {
                            console.error('Error:', error);
                        });
                    }
                }
            });

            socket.on("detection", (data: any) => {
                console.log("Detection: " + JSON.stringify(data));
               this.generateEvent("prediction", data);
            });

            socket.on("disconnect", () => {
                console.log("User disconnected");
            });
        });
    }

    public generateEvent(event: string, data: any) {
        try {
            this.io.emit(event, data);
        } catch (error) {
            console.log(error);
        }
    }
}