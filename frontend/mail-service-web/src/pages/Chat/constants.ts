export interface Message {
  id: number;
  authorId: number;
  content: string;
  numberOfAttachedFiles: number;
  createdTime: string;
  attachedFiles: File[];
}

export const messages: Message[] = [
  {
    id: 1,
    authorId: 0,
    content: 'some text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 2,
    authorId: 0,
    content: 'some text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 3,
    authorId: 0,
    content: 'some big text. some big text some big text some big text some big text some big text some big text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 4,
    authorId: 1,
    content: `some big text. some big text some big text some big text some big text some big text some big text
    some big text. some big text some big text some big text some big text some big text some big text`,
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 5,
    authorId: 0,
    content: 'some text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 6,
    authorId: 0,
    content: 'some text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 7,
    authorId: 0,
    content: 'some big text. some big text some big text some big text some big text some big text some big text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 8,
    authorId: 1,
    content: `some big text. some big text some big text some big text some big text some big text some big text
    some big text. some big text some big text some big text some big text some big text some big text`,
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 9,
    authorId: 1,
    content: `some big text. some big text some big text some big text some big text some big text some big text
    some big text. some big text some big text some big text some big text some big text some big text
    uaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`,
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 10,
    authorId: 0,
    content: 'some text 222 m,sfdhjgflisbjkf gso87efiluws',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 11,
    authorId: 0,
    content: 'some text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 12,
    authorId: 0,
    content: 'some text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 13,
    authorId: 0,
    content: 'some big text. some big text some big text some big text some big text some big text some big text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 14,
    authorId: 1,
    content: `some big text. some big text some big text some big text some big text some big text some big text
    some big text. some big text some big text some big text some big text some big text some big text`,
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 15,
    authorId: 0,
    content: 'some text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 16,
    authorId: 0,
    content: 'some text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 17,
    authorId: 0,
    content: 'some big text. some big text some big text some big text some big text some big text some big text',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 18,
    authorId: 1,
    content: `some big text. some big text some big text some big text some big text some big text some big text
    some big text. some big text some big text some big text some big text some big text some big text`,
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 19,
    authorId: 1,
    content: `some big text. some big text some big text some big text some big text some big text some big text
    some big text. some big text some big text some big text some big text some big text some big text
    uaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`,
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
  {
    id: 20,
    authorId: 0,
    content: 'some text 222 m,sfdhjgflisbjkf gso87efiluws',
    numberOfAttachedFiles: 0,
    createdTime: '01.01.2024',
    attachedFiles: []
  },
]
