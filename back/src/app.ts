// Imports & Configuration
import bodyParser from 'body-parser';
import express from 'express';
import cors from 'cors';
import compression from 'compression';
import cookieParser from 'cookie-parser';

// Socket
import { SocketSingleton } from './utils/socket';

// Request Interface
export interface Request extends express.Request {
  raw: any;
}

export class Application {

  public app: express.Application;
  private server: any;

  constructor() {
    this.app = express();
    this.config();
    this.routes();
    this.server = this.app.listen(process.env.PORT, () => {
      console.log(`Server running on port ${process.env.PORT}`);
    });
    this.socket();
  }

  private config(): void {
    this.app.use(function (req, res, next) {
      res.header('Access-Control-Allow-Credentials', 'true');
      res.header('Access-Control-Allow-Origin', req.headers.origin);
      res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE');
      res.header('Access-Control-Allow-Headers', 'X-Requested-With, X-HTTP-Method-Override, Content-Type, Accept, Set-Cookie, auth-token');
      if ('OPTIONS' == req.method) {
        res.sendStatus(200);
      } else {
        next();
      }
    });
    this.app.use(cookieParser());
    this.app.use(cors({ origin: true, credentials: true }));
    this.app.use(compression());
    this.app.use(bodyParser.raw());
    this.app.use(bodyParser.text());
    this.app.use(bodyParser.json());
    this.app.use(bodyParser.urlencoded({ extended: true }));
  }

  private routes(): void {

    this.app.use((req, res, next) => {
      console.log(`Request from: ${req.originalUrl}`);
      console.log(`Request type: ${req.method}`);
      next();
    });

    this.app.get('/', (req, res) => {
      res.status(200).send('Server is running!!');
    });
  }

  private socket(): void {
    console.log("Creating socket instance");
    SocketSingleton.createInstance(this.server);
  }
}