/// <reference types="node" />
import { IncomingMessage } from 'http';
import { VercelProxyResponse } from '@vercel/node-bridge/types';
export declare function createEdgeEventHandler(entrypointPath: string, entrypointLabel: string, isMiddleware: boolean): Promise<(request: IncomingMessage) => Promise<VercelProxyResponse>>;
