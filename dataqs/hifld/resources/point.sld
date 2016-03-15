<?xml version="1.0" encoding="UTF-8"?>
<sld:StyledLayerDescriptor
        xmlns="http://www.opengis.net/sld"
        xmlns:sld="http://www.opengis.net/sld"
        xmlns:ogc="http://www.opengis.net/ogc"
        xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>{table}</sld:Name>
    <sld:UserStyle>
      <sld:Name>{table}</sld:Name>
      <sld:Title>{title}</sld:Title>
      <sld:FeatureTypeStyle>
        <sld:Name>{title}</sld:Name>
        <sld:Rule>
          <sld:PointSymbolizer>
            <sld:Graphic>
              <sld:Mark>
                <sld:WellKnownName>x</sld:WellKnownName>
                <sld:Fill>
                  <sld:CssParameter name="fill">#888800</sld:CssParameter>
                </sld:Fill>
                <sld:Stroke>
                  <sld:CssParameter name="stroke">#ffffbb</sld:CssParameter>
                </sld:Stroke>
              </sld:Mark>
              <sld:Size>10</sld:Size>
            </sld:Graphic>
          </sld:PointSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
