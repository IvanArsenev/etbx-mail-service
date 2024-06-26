export interface Message {
  id: string;
  subject: string;
  body: string;
  sender: string;
  recipient: string;
  received_time: string;
  files: File[];
}
