import useSettings from "app/hooks/useSettings";

export default function MatxLogo({ className }) {
  const { settings } = useSettings();
  const theme = settings.themes[settings.activeTheme];

  return (
  <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="80" height="70.9162561576354" viewBox="0 0 1300.783251231527 738.9162561576354">
    <g transform="scale(10.389162561576355) translate(30, 10)">
      <defs id="SvgjsDefs1378">
        <linearGradient id="SvgjsLinearGradient1385">
          <stop id="SvgjsStop1386" stop-color="#00ff8f" offset="0"/>
          <stop id="SvgjsStop1387" stop-color="#00a1ff" offset="1"/>
        </linearGradient>
      </defs>
      <g id="SvgjsG1379" featureKey="symbolFeature-0" transform="matrix(20.70760938725105,0,0,20.70760938725105,-19.382323403505218,-11.77316365304414)" fill="url(#SvgjsLinearGradient1385)">
        <g xmlns="http://www.w3.org/2000/svg">
          <g>
            <polygon fill="url(#SvgjsLinearGradient1385)" points="2.107,4.191 2.789,4.191 4.066,3.203 4.066,1.564 3.217,0.81 1.725,2.129 1.725,2.705     2.059,3.001 2.434,2.668 2.25,2.507 2.25,2.282 3.236,1.411 3.576,1.712 3.576,3.027   "/>
          </g>
          <g>
            <polygon fill="url(#SvgjsLinearGradient1385)" points="2.893,0.81 2.211,0.81 0.936,1.798 0.936,3.437 1.785,4.191 3.275,2.87 3.275,2.295 2.941,1.999     2.568,2.332 2.75,2.493 2.75,2.718 1.764,3.589 1.426,3.29 1.426,1.972   "/>
          </g>
        </g>
      </g>
      <g id="SvgjsG1380" fill="#cee4fb">
        <rect xmlns="http://www.w3.org/2000/svg" y="0" height="1" width="1" opacity="0"/>
        <rect xmlns="http://www.w3.org/2000/svg" y="0" x="-320" width="3" height="80"/>
      </g>
      <g id="SvgjsG1381" featureKey="nameFeature-0" transform="matrix(1.1778026326017637,0,0,1.1778026326017637,100.64677867154724,8.316202287691777)">
        <path d=""/>
      </g>
    </g>
  </svg>
  );
}
