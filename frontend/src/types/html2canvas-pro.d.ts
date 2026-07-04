declare module "html2canvas-pro" {
  import type { Options as Html2CanvasOptions } from "html2canvas";

  function html2canvas(element: HTMLElement, options?: Partial<Html2CanvasOptions>): Promise<HTMLCanvasElement>;
  export default html2canvas;
}
