import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div className={`prose prose-sm max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkBreaks]}
        components={{
          // Code blocks with syntax highlighting
          code(props) {
            const { children, className, ...rest } = props;
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            
            if (language) {
              return (
                <SyntaxHighlighter
                  style={oneDark as any}
                  language={language}
                  PreTag="div"
                  className="rounded-lg !mt-2 !mb-4"
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              );
            }
            
            // Inline code
            return (
              <code
                className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono"
                {...rest}
              >
                {children}
              </code>
            );
          },
          
          // Headings with proper styling
          h1(props) {
            return (
              <h1 className="text-2xl font-bold text-gray-900 mt-6 mb-4 first:mt-0">
                {props.children}
              </h1>
            );
          },
          h2(props) {
            return (
              <h2 className="text-xl font-semibold text-gray-900 mt-5 mb-3 first:mt-0">
                {props.children}
              </h2>
            );
          },
          h3(props) {
            return (
              <h3 className="text-lg font-semibold text-gray-900 mt-4 mb-2 first:mt-0">
                {props.children}
              </h3>
            );
          },
          h4(props) {
            return (
              <h4 className="text-base font-semibold text-gray-900 mt-3 mb-2 first:mt-0">
                {props.children}
              </h4>
            );
          },
          h5(props) {
            return (
              <h5 className="text-sm font-semibold text-gray-900 mt-3 mb-2 first:mt-0">
                {props.children}
              </h5>
            );
          },
          h6(props) {
            return (
              <h6 className="text-sm font-medium text-gray-900 mt-3 mb-2 first:mt-0">
                {props.children}
              </h6>
            );
          },
          
          // Paragraphs
          p(props) {
            return (
              <p className="text-gray-700 mb-3 leading-relaxed">
                {props.children}
              </p>
            );
          },
          
          // Lists
          ul(props) {
            return (
              <ul className="list-disc list-inside mb-3 space-y-1 text-gray-700">
                {props.children}
              </ul>
            );
          },
          ol(props) {
            return (
              <ol className="list-decimal list-inside mb-3 space-y-1 text-gray-700">
                {props.children}
              </ol>
            );
          },
          li(props) {
            return (
              <li className="text-gray-700">
                {props.children}
              </li>
            );
          },
          
          // Links
          a(props) {
            const { href, children } = props;
            return (
              <a
                href={href}
                target={href?.startsWith('http') ? '_blank' : undefined}
                rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
                className="text-blue-600 hover:text-blue-800 underline"
              >
                {children}
              </a>
            );
          },
          
          // Blockquotes
          blockquote(props) {
            return (
              <blockquote className="border-l-4 border-blue-200 pl-4 py-2 mb-3 bg-blue-50 text-gray-700 italic">
                {props.children}
              </blockquote>
            );
          },
          
          // Tables
          table(props) {
            return (
              <div className="overflow-x-auto mb-4">
                <table className="min-w-full border border-gray-200 rounded-lg">
                  {props.children}
                </table>
              </div>
            );
          },
          thead(props) {
            return (
              <thead className="bg-gray-50">
                {props.children}
              </thead>
            );
          },
          tbody(props) {
            return (
              <tbody className="divide-y divide-gray-200">
                {props.children}
              </tbody>
            );
          },
          tr(props) {
            return <tr>{props.children}</tr>;
          },
          th(props) {
            return (
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-900 border-b border-gray-200">
                {props.children}
              </th>
            );
          },
          td(props) {
            return (
              <td className="px-4 py-2 text-sm text-gray-700">
                {props.children}
              </td>
            );
          },
          
          // Horizontal rule
          hr() {
            return <hr className="border-gray-200 my-6" />;
          },
          
          // Strong and emphasis
          strong(props) {
            return (
              <strong className="font-semibold text-gray-900">
                {props.children}
              </strong>
            );
          },
          em(props) {
            return (
              <em className="italic text-gray-700">
                {props.children}
              </em>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

export default MarkdownRenderer;
